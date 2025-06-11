import re

from fastapi import Depends, HTTPException, Query, status
from langchain.chains import create_sql_query_chain
from langchain.prompts import ChatPromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from sqlalchemy import text
from sqlalchemy.orm import Session

from smartsales.core.database import get_session
from smartsales.core.security import (
    get_current_user,
)
from smartsales.core.settings import Settings
from smartsales.schemas.auth_schema import UserInfo
from smartsales.schemas.search_schema import SearchCreate, SearchOut
from smartsales.services.search_service import SearchService

settings = Settings()

# ─── 1) DEPENDÊNCIA OPCIONAL PARA LER O JWT ────────────────────────────────
# – Se vier o Bearer token, decodifica e retorna um UserInfo; retorna None.
# bearer_scheme = HTTPBearer(bearerFormat='JWT', auto_error=False)


# async def get_current_user_optional(
#     credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
# ) -> UserInfo | None:
#     if credentials and credentials.credentials:
#         # “get_current_user” deve lançar exceção caso o token seja inválido
#         return get_current_user(credentials.credentials)
#     return None


# ─── 2) TEMPLATE COM AS REGRAS DE NEGÓCIO (CLIENTS, PRODUCTS, ORDERS) ───────
BUSINESS_RULES_TEMPLATE = """
Você é um especialista em regras de negócio do sistema SmartSales.
Responda APENAS com base nas seguintes informações:

=== ENTIDADES DO SISTEMA ===

1. Auth (Usuário)
   - Campos: id, name, email, password, role (admin/user), created_at, updated_at
   - Relacionamentos: É o dono (owner) de clientes, produtos e pedidos.

2. Client (Clientes)
   - Campos: id, name, email, cpf, owner_id, created_at, updated_at
   - Relacionamentos:
       • owner → Auth (um cliente pertence a um usuário)
       • orders → lista de pedidos (Order) desse cliente.

3. Product (Produtos)
   - Campos: id, title, sale_price, section, description, barcode, stock, expiry_date, images, owner_id
   - Relacionamentos:
       • owner → Auth (um produto pertence a um usuário)
       • order_items → vínculo com OrderItem (quantidade, unit_price, total_price).

4. Order (Pedidos)
   - Campos: id, client_id, total_value, status (pending/confirmed/shipped/delivered/canceled), owner_id, created_at, updated_at
   - Relacionamentos:
       • client → Client (pedido feito por um cliente)
       • owner → Auth (pedido criado por um usuário)
       • items → lista de OrderItem (cada item vincula produto + quantidade + preço)

5. OrderItem (Itens de Pedido)
   - Campos: id, order_id, product_id, quantity, unit_price, total_price, created_at, updated_at
   - Relacionamentos:
       • order → Order (pertence a um pedido)
       • product → Product (produto vendido no pedido)

=== REGRAS DE NEGÓCIO PRINCIPAIS ===
- Todo cliente, produto e pedido pertence a um único usuário (campo owner_id).
- Pedidos só podem mudar de status em etapas válidas (e.g. não dá para passar
de “delivered” de volta para “pending”).
- Ao criar/atualizar produto, validar se o usuário (owner)
realmente possui esse produto.
- Ao criar pedido, certificar que todos os itens existem em estoque.
- Um usuário com role “user” NÃO pode excluir produtos ou pedidos
de outros usuários.
- Somente “admin” pode ver/alterar pedidos de outros usuários, mas pode
consultar qualquer cliente/produto.

Pergunta do usuário: {query}
"""  # noqa: E501


def extract_sql_query(generated_text: str) -> str:
    """Extrai a consulta SQL do texto gerado pelo LLM"""
    # Tenta encontrar blocos de código SQL
    sql_match = re.search(r'```sql(.*?)```', generated_text, re.DOTALL)
    if sql_match:
        return sql_match.group(1).strip()

    # Tenta encontrar comandos SQL simples
    sql_match = re.search(
        r'(SELECT.*?;)', generated_text, re.DOTALL | re.IGNORECASE
    )
    if sql_match:
        return sql_match.group(1).strip()

    return generated_text.strip()


def is_valid_sql(query: str) -> bool:
    return query.lower().strip().startswith(('select', 'with'))


async def search_query(  # noqa: PLR0914
    q: str = Query(
        ..., min_length=3, max_length=255, description='Texto de busca'
    ),
    database: bool = Query(
        False, description='Realizar consulta direta no banco de dados'
    ),
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> SearchOut:
    """
    1) Recebe o parâmetro `q` na query-string (ex: /api/search?q=Texto).
    2) Identifica se há user autenticado (current_user) ou não
    (owner_id = None).
    3) Monta o prompt com BUSINESS_RULES_TEMPLATE.format(query=q).
    4) Chama o LLM (ChatGroq) para responder baseado nas regras de negócio.
    5) Salva a pesquisa no banco (query + resposta + owner_id).
    6) Retorna SearchOut (id, query, response, owner_id, created_at).
    """
    # 1) Se database=True, usar fluxo de consulta direta ao banco
    if database:
        # Verificar se pacotes necessários estão instalados
        if not all([SQLDatabase, create_sql_query_chain, ChatPromptTemplate]):
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail='Requer instalação de langchain e langchain-community',
            )

        try:
            # Configurar conexão com o banco
            engine = db.get_bind()
            sql_db = SQLDatabase(engine)

            # Gerar consulta SQL natural language
            llm_sql = ChatGroq(
                model='llama-3.3-70b-versatile',
                api_key=settings.GROQ_API_KEY,
                temperature=0,
            )
            chain = create_sql_query_chain(llm_sql, sql_db)
            generated_text = chain.invoke({'question': q})

            # Extrair e validar a consulta SQL
            generated_query = extract_sql_query(generated_text)

            if not is_valid_sql(generated_query):
                raise ValueError(
                    f'Consulta SQL inválida gerada: {generated_query}'
                )

            # Executar consulta SQL com transação segura
            try:
                result = db.execute(text(generated_query)).fetchall()
                result_str = '\n'.join(str(row) for row in result)
            except Exception as e:
                db.rollback()  # Importante para limpar transações abortadas
                raise RuntimeError(
                    f'Erro na execução da consulta: {str(e)}'
                ) from e

            # Interpretar resultados com LLM
            prompt_template = ChatPromptTemplate.from_messages([
                (
                    'system',
                    'Você é um especialista em SQL. Explique os resultados:',
                ),
                (
                    'human',
                    'Pergunta: {question}\nConsulta: {query}\nResultados:\n{result}',  # noqa: E501
                ),
            ])

            llm_final = ChatGroq(
                model='llama-3.3-70b-versatile',
                api_key=settings.GROQ_API_KEY,
                temperature=0.2,
            )
            print(f'RESPOSTA Consultads no SQL:\n {generated_query}\n')
            print(f'RESPOSTA DO DB:\n {result_str}\n')

            chain_final = prompt_template | llm_final
            response = chain_final.invoke({
                'question': q,
                'query': generated_query,
                'result': result_str,
            })

            response_text = response.content

        except Exception as e:
            response_text = f'Erro na consulta ao banco: {str(e)}'
            db.rollback()  # Garante limpeza da transação em caso de erro

    # 2) Fluxo padrão (sem database=true)
    else:
        system_message = BUSINESS_RULES_TEMPLATE.format(query=q)
        try:
            chat = ChatGroq(
                model='llama-3.3-70b-versatile',
                api_key=settings.GROQ_API_KEY,
                temperature=0.2,
            )
            messages = [
                {'role': 'system', 'content': system_message},
                {'role': 'user', 'content': q},
            ]
            response = chat.invoke(messages)
            response_text = response.content

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Erro ao processar busca: {e}',
            )

    print(f'REPOSTA TEXTO IA: \n{response_text}')
    # Salvar no banco e retornar
    search_in = SearchCreate(query=q, database=database)
    owner_id = current_user.id if current_user else None

    saved = SearchService.create_search(
        db=db,
        search_in=search_in,
        response=response_text,
        owner_id=owner_id,
    )
    return saved
