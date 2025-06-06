from fastapi import Depends, HTTPException, Query, status
from langchain_groq import ChatGroq
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


async def search_query(
    q: str = Query(
        ..., min_length=3, max_length=255, description='Texto de busca'
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
    # 1) Montar o “system prompt” completo
    system_message = BUSINESS_RULES_TEMPLATE.format(query=q)

    try:
        # 2) Instanciar ChatGroq
        chat = ChatGroq(
            model='llama-3.3-70b-versatile',
            api_key=settings.GROQ_API_KEY,
            # temperatura baixa para respostas mais determinísticas
            temperature=0.2,
            max_retries=2,
        )

        # 3) Enviar “system” + “user” messages
        messages = [
            {'role': 'system', 'content': system_message},
            {'role': 'user', 'content': q},
        ]
        # Use invoke() em vez de __call__() para não receber warnings
        llm_response = chat.invoke(messages)

        # 3) Extrai o texto de forma robusta
        if hasattr(llm_response, 'content'):
            # Quando retornar um objeto (não dict), ele terá .content
            response_text = llm_response.content

        elif isinstance(llm_response, dict):
            # Quando for dict, tentamos achar choices→message→content
            try:
                response_text = llm_response['choices'][0]['message'][
                    'content'
                ]  # noqa: E501
            except (KeyError, IndexError, TypeError):
                response_text = str(llm_response)

        else:
            # Qualquer outro formato, cai aqui
            response_text = str(llm_response)

        print(f'RESPOSTA CHAT Result: {llm_response} ')

        print(f'RESPOSTA CHAT LLM TEXT: {response_text} ')

        # 4) Salvar no banco
        search_in = SearchCreate(query=q)
        owner_id = current_user.id

        saved = SearchService.create_search(
            db=db,
            search_in=search_in,
            response=response_text,
            owner_id=owner_id,
        )

        return saved

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Erro ao processar busca: {e}',
        )
