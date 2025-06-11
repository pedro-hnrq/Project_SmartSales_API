# Project_SmartSales_API

<p align="center">
<a href="#-prévia">Prévia</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="#-objetivo">Objetivo</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="#-pré-requisitos">Instalação</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="#-tasks">Comados no Terminal</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="#️-apis">API Rest</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="#-dbeaver---postgresql">Banco de Dados</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="#-docker">Docker</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
    <a href="#-teste-unitário">Testes Unitários</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="#licença">Licença</a>
</p>

### 📷 Prévia

![smartsales](https://github.com/user-attachments/assets/735e6ee8-223c-4d84-81c3-0ddf240bbab4)


#### 🎯 Objetivo

Este projeto tem como objetivo demonstrar a construção de uma API REST robusta utilizando autenticação JWT (JSON Web Token), com controle de acesso baseado em papéis (roles), sendo eles `admin` (administrador) e `user` (usuário regular). A API é estruturada para gerenciar entidades fundamentais como `clients` (clientes), `products` (produtos) e `orders` (pedidos), garantindo segurança, organização e escalabilidade no acesso e manipulação dos dados.

Além das funcionalidades tradicionais de CRUD, o projeto implementa uma funcionalidade de _pesquisa inteligente com LLM_ (Large Language Model – Modelo de Linguagem de Grande Escala), integrando o modelo _LLaMA 3.3 70B_ por meio da plataforma _Groq_. Essa integração permite que os usuários façam perguntas em linguagem natural sobre regras de negócio e recebam respostas contextualizadas e precisas, simulando uma interação com um assistente virtual corporativo.

#### 💻 Pré-requisitos

Antes de começar, verifique se você atendeu aos seguintes requisitos:

- Python 
- FastAPI
- Poetry
- GIT 
- PostgreSQL
- Docker
- Docker Compose


#### 🛠️ Instalação

Faça o clone do projeto:
```bash
git clone git@github.com:pedro-hnrq/Project_SmartSales.git
```

Após clonar o repositório acesse o diretório:
```bash
cd Project_SmartSales_API
``` 

Modifique o arquivo `.env-exemple` para `.env`.
```bash
mv env-exemple .env
```

Na parte para colocar o key no no .env de `GROQ_API_KEY` poderá acessar o site <a href="https://console.groq.com/login">Groq</a>. Criando a conta, depois gerando a chave.



Uma vez criado seu ambiente virtual, você deve ativá-lo.

```bash
poetry env activate
```
Quiser executa com `poetry shell` com o pipx

```bash
pipx inject poetry poetry-plugin-shell
```

```bash
poetry shell
```

Instalar as depêndencias:

```bash
poetry install
```

Realiza as migrações no Banco de Dados - PostgreSQL

```python
alembic upgrade head
```

Ruff - Linter e Format

```python
ruff linter
```
```python
ruff format
```

#### 🪢 Tasks

Atalho que poderá utilizar no terminal.

 | **Descrição**   | **Comando** | 
|------------|-----------|
| Linter        |  ```task lint ``` | 
|  Pré Formato | ```task pre_format ```   | 
| Formato     | ```task format ```   | 
| Execução do Projeto       |  ```task run ``` | 
|  Pre Teste | ```task pre_test ```   | 
| Teste     | ```task test ```  | 
| Coverage     | ```task post_test ```  | 


#### 🗺️ APIs

 - Swagger: `localhost:8000/doc/`
 - Redoc: `localhost:8000/redoc`

🔐 **Autenticação** - JWT
 
 Antes de começarmos a interagir com a API, precisamos obter um token de acesso JWT (JSON Web Token). Esse token é como uma chave que garante que você tenha permissão para acessar os recursos protegidos da API.

 | **Método**   | **Endpoint** | **Descrição** |  **Autenticação** |
|------------|-----------|------------------|------------------|
| POST       |  `/api/token/login` | Realizar login   |  NÃO  |
|  POST | `/api/token/register/`   | Registar na plataforma   |  NÃO |
| POST     | `/api/token/refresh-token/`   | Obter access_token |  NÃO |

⚠️ Níveis de Acesso (Roles) 

Existem dois níveis de acesso principais para os endpoints:

- `admin` (Administrador): Usuários com este perfil têm acesso total e irrestrito a todos os endpoints de produtos. Eles podem listar, visualizar, criar, atualizar e deletar qualquer produto no sistema.
- `user` (Usuário Regular): Usuários com este perfil podem:
    - Listar (GET /api/products/) e visualizar (GET /api/products/{id}/) todos os produtos.
    - Criar (POST /api/products/) novos produtos.
    - Atualizar (PUT /api/products/{id}/) e deletar (DELETE /api/products/{id}/) apenas os produtos que eles mesmos criaram. Tentativas de modificar ou deletar produtos de outros usuários resultarão em um erro de acesso não autorizado (geralmente um status 403 Forbidden ou 404 Not Found dependendo da implementação).

 _Lembre-se_:

- O token JWT tem validade de um dia e duração de 30 minutos. Após esse período, você precisará renová-lo usando o endpoint `POST /api/token/refresh-token/`.

 1. Criar um admin/user: 

    Endpoint: `POST /api/auth/register`
    
    Role: admin
    ```
    {
        "name": "Alan Bery",
        "email": "alby@mail.com",
        "password": "Alb.1234",
        "role": "admin"
    }
    ```
    Role: user
    ```
     {
        "name": "Jack Run",
        "email": "runj@mail.com",
        "password": "Run.1234",
        "role": "user"
    }
    ```
    Sucesso da resposta (201 Created)
    ```
    {
        "name": "Alan Bery",
        "email": "alby@mail.com",
        "role": "admin"
    }
    ```

    ```
    {
        "name": "Jack Run",
        "email": "runj@mail.com",
        "role": "user"
    }
    ```
2. Login:

    Endpoint: `POST /api/auth/login`

    ```
    {
        "email": "runj@mail.com",
        "password": "Run.1234"
    }
    ```

    Sucesso da resposta (200 OK)
    ```
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJydW5qQG1haWwuY29tIiwiaWF0IjoxNzQ4Mjg3MjY1LCJleHAiOjE3NDgyODkwNjV9.E2dloj6unoWs3mALkGjnJSSKD74ScuR_ehZ4HyBzSz4",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJydW5qQG1haWwuY29tIiwiZXhwIjoxNzQ4ODkyMDY1fQ.l1a62SQJ4gWS3YXqCoJWFywlGZSpXnAx32KPYeTJMU0",
        "token_type": "Bearer",
        "exp": 1748289065,
        "iat": 1748287265,
        "user": {
            "id": 4,
            "email": "runj@mail.com",
            "role": "user"
        }
    }
    
    ```
3. Refresh Token

    Endpoint: `POST /api/auth/refresh-token`

    ```
    {
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJydW5qQG1haWwuY29tIiwiZXhwIjoxNzQ4ODkyMD
    }
    ```
    Sucesso da resposta (200 OK)

    ```
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGJ5QG1haWwuY29tIiwiaWF0IjoxNzQ4Mjg4MDAxLCJleHAiOjE3NDgyODk4MDF9.LQf2sxq7TzTdVhJ_OEizHnGFOAjzURWn9rKCtdO69wc"
    }
    ```

🔍 **Pesquisa (LLM + Groq)**

Utilizando o LLM - Groq (Llama 3.3 70B Versatile) para responder perguntas sobre as regras de negócio do SmartSales e salvar cada consulta no banco de dados.

 | **Método**   | **Endpoint** | **Descrição** |  **Autenticação** |
|------------|-----------|------------------|------------------|
| GET       |  `/api/search/` | Obter informação SmartSales    |  SIM  |


Necessita está autenticado para acessar os endpoints. Pois o retorno da resposta status (401 Unauthorized).
```
{
    "detail": "Could not validate credentials"
}
```

1. Obter informações na pesquisa:

    Endpoint `GET /api/search/`
    
    Params `?q="Traga o nome e cpf de todos os clientes cadastrados"&database=true`

    | **Key**   | **Value** | **Discription** |  
    |------------|-----------|------------------|
    | q     |  Traga o nome e cpf de todos os clientes cadastrados | Pergunta que deseja obter |
    | database     |  true/false | Utilizar as informações do banco de dados |
    
   
    Resposta (200 OK)
    ````
    {
        "query": "Traga o nome e cpf de todos os clientes cadastrados",
        "database": true,
        "id": 2,
        "response": "**Análise da Consulta SQL**\n\nA consulta SQL fornecida é:\n```sql\nSELECT \"name\", \"cpf\" FROM clients LIMIT 5;\n```\nEssa consulta tem como objetivo trazer o nome e o CPF de todos os clientes cadastrados na tabela `clients`. No entanto, há um detalhe importante a considerar: a cláusula `LIMIT 5`.\n\n**O que significa a cláusula LIMIT?**\n\nA cláusula `LIMIT` é usada para limitar o número de linhas retornadas pela consulta. Nesse caso, `LIMIT 5` significa que a consulta retornará apenas as 5 primeiras linhas da tabela `clients`, e não todos os clientes cadastrados.\n\n**Resultados**\n\nOs resultados da consulta são:\n```markdown\n('Jonas Brother', '23228592065')\n('Carla Ruy', '46036111029')\n('Joaquim Andre', '11792319029')\n```\nObserve que a consulta retornou apenas 3 linhas, e não 5. Isso pode ocorrer por várias razões, como:\n\n* A tabela `clients` tem menos de 5 linhas.\n* A consulta foi interrompida antes de retornar todas as 5 linhas.\n* Há um erro na consulta ou na tabela.\n\n**Conclusão**\n\nEm resumo, a consulta SQL fornecida não traz o nome e o CPF de todos os clientes cadastrados, mas sim apenas as 5 primeiras linhas da tabela `clients`. Se você deseja trazer todos os clientes, é necessário remover a cláusula `LIMIT 5` da consulta:\n```sql\nSELECT \"name\", \"cpf\" FROM clients;\n```\nEssa consulta retornará todos os clientes cadastrados na tabela `clients`.",
        "owner_id": 2,
        "created_at": "2025-06-11T19:23:21.049999"
    }
    
    ```

🛗 **Clientes**

 | **Método**   | **Endpoint** | **Descrição** |  **Autenticação** |
|------------|-----------|------------------|------------------|
| GET       |  `/api/clients/` | Listar somente a clientes    |  SIM  |
|  GET | `/api/clients/:id/`   | Obter com ID a clientes   |  SIM |
| POST     | `/api/clients/`   | Criar novo clientes |  SIM |
|  PUT | `/api/clients/:id/`   | Atualizar registro de clientes   | SIM  |
| DELETE     | `/api/clients/:id/`   | Deleta registro do clientes | SIM  |

Necessita está autenticado para acessar os endpoints. Pois o retorno da resposta status (401 Unauthorized).
```
{
    "detail": "Could not validate credentials"
}
```

1. Criar um cliente:

    Endpoint: `POST /api/clients/`
    ```
    {
        "name": "Felipe Eduardo",
        "email": "feed@example.com",
        "cpf": "14391150018"
    }
    ```
    Sucesso da resposta (201 Created)
    ```
    {
        "name": "Felipe Eduardo",
        "email": "feed@example.com",
        "cpf": "14391150018",
        "id": 3,
        "owner": {
            "email": "devu@mail.com",
            "role": "user"
        }
    }
    ``` 


2. Listar clientes:

    Endpoint `GET /api/clients/`

    Params `?skip=0&limit=10&name=Felipe&email=feed%40example.com`

    | **Key**   | **Value** | **Discription** |  
    |------------|-----------|------------------|
    | skip     |  0 | Ignorar número de registros |
    |  limit | 10   | Numero máximo de limite |
    | name     | Felipe   | nome do cliente |
    |  email | feed@example.com   | client@mail.com   |
    
   
    Sucesso da resposta (200 OK)
    ```
    {
        "total": 1,
        "items": [
            {
            "name": "Felipe Eduardo",
            "email": "feed@example.com",
            "cpf": "14391150018",
            "id": 3,
            "owner": {
                "email": "devu@mail.com",
                "role": "user"
            }
            }
        ]
    }    
    ```


3. Obter cliente por ID:
    
    Se autenticado como role=user e colocar um ID de cliente que não seja o do próprio usuário, retorná na requisição 403 - Forbidden.

    ```
    {
        "detail": "Not authorized to access this client"
    }
    ```

    Endpoint `GET /api/clients/:id/`, ID = 2
    
    Sucesso da Resposta (200 OK)
    ```
    {
        "name": "Lucas ScalWork",
        "email": "skork@example.com",
        "cpf": "12513945077",
        "id": 2,
        "owner": {
            "email": "devu@mail.com",
            "role": "user"
        }
    }
    ```



4. Atualizar um cliente:

    Endpoint: `PUT /api/clients/:id/`, ID = 2

    Sucesso da resposta (200 OK)
    ```
    {
        "name": "Lucas Parker",
        "email": "lucas@mail.com",
        "cpf": "12513945077",
        "id": 2,
        "owner": {
            "email": "devu@mail.com",
            "role": "user"
        }
    }
    
    ```

5. Deletar um cliente:

    Endpoint: `DELETE /api/clients/:id/`, ID = 3

    Sucesso da resposta (204 No Content)
    

🎱 **Produtos**

 | **Método**   | **Endpoint** | **Descrição** |  **Autenticação** |
|------------|-----------|------------------|------------------|
| GET       |  `/api/products/` | Listar somente a produtos    |  SIM  |
|  GET | `/api/products/:id/`   | Obter com ID a produtos   |  SIM |
| POST     | `/api/products/`   | Criar novo produtos |  SIM |
|  PUT | `/api/products/:id/`   | Atualizar registro de produtos   | SIM  |
| DELETE     | `/api/products/:id/`   | Deleta registro do produtos | SIM  |

Necessita está autenticado para acessar os endpoints. Pois o retorno da resposta status (401 Unauthorized).
```
{
    "detail": "Could not validate credentials"
}
```


1. Criar um produtos:

    Endpoint: `POST /api/products/` (Body: form-data)

    | **Key**   |  | **Value** |  
    |------------|-----------|------------------|
    | title       |  Text | TV LG 55 4K |
    |  sale_price | Text   | 6799.89 |
    | section     | Text   | Móveis |
    |  description | Text   | Mega Sofa Cama   |
    | barcode     | Text   | 456489419 |
    | stock       |  Text | 17 |
    |  expiry_date | Text   | 2025-06-25 |
    | images     | File   | TV-LG-55-4K.jpg, TV-LG-55-4K_.jpg |

    Sucesso da resposta (201 Created)
    ```
    {
        "title": "TV LG 55 4K",
        "sale_price": 6799.89,  
        "section": "Móveis",
        "id": 5,
        "description": "Mega Sofa Cama",
        "barcode": "456489419",
        "stock": 17,
        "expiry_date": "2025-06-25",
        "images": [
            "static/uploads/TV-LG-55-4K.jpg",
            "static/uploads/TV-LG-55-4K_.jpg"
        ],
        "owner": {
            "name": "Dev Admin",
            "email": "dev@mail.com",
            "role": "admin"
        }
    }
    ```     

2. Listar produtos:

    Endpoint `GET /api/products/`
    
    Params `?skip=0&limit=10&section=Eletrodoméstico&price_min=100&price_max=15000&available=true`

    | **Key**   | **Value** | **Discription** |  
    |------------|-----------|------------------|
    | skip     |  0 | Ignorar número de registros |
    |  limit | 10   | Numero máximo de limite |
    | section     | Eletrodoméstico   | Eletrodoméstico, Eletrônica, Móveis |
    |  price_min | 500   | Valor Mínimo   |
    | price_max     | 30000   | Valor Máximo |
    | available       |  true | Stock/Estoque = 0 (false) e Stock/Estoque > 0 (true) |
   
    Resposta (200 OK)
    ```
    {
        "total": 2,
        "items": [
            {
            "title": "TV LG 55 4K",
            "sale_price": 2899,
            "section": "Eletrodoméstico",
            "id": 5,
            "description": "Smart TV LG NanoCell NANO80 4K de 55 polegadas (55NANO80) oferece uma experiência visual imersiva com a tecnologia NanoCell, que aprimora as cores e o contraste para uma imagem mais rica e detalhada.",
            "barcode": "456489419",
            "stock": 17,
            "expiry_date": "2025-06-15",
            "images": [
                "static/uploads/TV-LG-55-4K_2.jpg"
            ],
            "owner": {
                "name": "Dev Admin",
                "email": "dev@mail.com",
                "role": "admin"
                }
            },
            {
            "title": "MacBook Air 4",
            "sale_price": 22469.55,
            "section": "Eletrodoméstico",
            "id": 6,
            "description": "Apple Macbook Air 15\", M4, com CPU de 10 núcleos, GPU de 10 núcleos, 24GB RAM, 512GB SSD - Prata",
            "barcode": "756489489",
            "stock": 0,
            "expiry_date": "2025-06-02",
            "images": [
                "static/uploads/macbook-air-m4.png"
            ],
            "owner": {
                "name": "Dev User",
                "email": "devu@mail.com",
                "role": "user"
                }
            }
        ]
    }    
        
    ```

3. Obter produtos por ID:

    Endpoint ``GET /api/products/:product_id/`, product_id = 5

    Resposta (200 OK)

    ```
    {
        "title": "TV LG 55 4K",
        "sale_price": 2899.0,
        "section": "Eletrodoméstico",
        "id": 5,
        "description": "Smart TV LG NanoCell NANO80 4K de 55 polegadas (55NANO80) oferece uma experiência visual imersiva com a tecnologia NanoCell, que aprimora as cores e o contraste para uma imagem mais rica e detalhada.",
        "barcode": "456489419",
        "stock": 17,
        "expiry_date": "2025-06-15",
        "images": [
            "static/uploads/TV-LG-55-4K_2.jpg"
        ],
        "owner": {
            "name": "Dev Admin",
            "email": "dev@mail.com",
            "role": "admin"
        }
    }
    
    ```

4. Atualizar um produtos:

    Endpoint: `PUT /api/products/:product_id/` (Body: form-data)

    | **Key**   |  | **Value** |  
    |------------|-----------|------------------|
    | title       |  Text | TV LG 55 4K |
    |  sale_price | Text   | 6799.89 |
    | section     | Text   | Eletrodoméstico |
    |  description | Text   | Smart TV LG NanoCell NANO80 4K de 55 polegadas |
    | barcode     | Text   | 456489419 |
    | stock       |  Text | 17 |
    |  expiry_date | Text   | 2025-06-25 |
    | images     | File   | TV-LG-55-4K_2.jpg |


    Sucesso da resposta (200 Ok)
    ```
    {
    "title": "TV LG 55 4K",
    "sale_price": 2899,
    "section": "Eletrodoméstico",
    "id": 5,
    "description": "Smart TV LG NanoCell NANO80 4K de 55 polegadas",
    "barcode": "456489419",
    "stock": 17,
    "expiry_date": "2025-06-15",
    "images": [
        "static/uploads/TV-LG-55-4K_2.jpg"
    ],
    "owner": {
        "name": "Dev Admin",
        "email": "dev@mail.com",
        "role": "admin"
        }
    }
    ```  

5. Deletar um produtos:

    Endpoint: `DELETE /api/products/:product_id/`, product_id = 7

    A resposta (204 No Content)


⛳ **Pedidos**

 | **Método**   | **Endpoint** | **Descrição** |  **Autenticação** |
|------------|-----------|------------------|------------------|
| GET       |  `/api/orders/` | Listar somente a pedidos    |  SIM  |
|  GET | `/api/orders/:id/`   | Obter com ID a pedidos   |  SIM |
| POST     | `/api/orders/`   | Criar novo pedidos |  SIM |
|  PUT | `/api/orders/:id/`   | Atualizar registro de pedidos   | SIM  |
| DELETE     | `/api/orders/:id/`   | Deleta registro do pedidos | SIM  |


Necessita está autenticado para acessar os endpoints. Pois o retorno da resposta status (401 Unauthorized).
```
{
    "detail": "Could not validate credentials"
}
```

1. Criar um pedido:

    Endpoint: `POST /api/orders/`
    ```
    {
    "client_id": 2,
    "status": "shipped",
    "items": [
            {
                "product_id": 1,
                "quantity": 1
            }
        ]
    }
    ```
    Sucesso da resposta (200 Ok)
    ```
    {
        "id": 4,
        "client_id": 2,
        "status": "shipped",
        "total_value": "2890.00",
        "items": [
            {
            "id": 5,
            "product_id": 1,
            "quantity": 1,
            "unit_price": "2890.00",
            "total_price": "2890.00"
            }
        ],
        "owner": {
            "name": "Dev User",
            "email": "devu@mail.com",
            "role": "user"
        },
        "created_at": "2025-06-06T18:48:47.720315",
        "updated_at": "2025-06-06T18:48:47.720315"
    }
    ```

2. Listar pedidos:

    Endpoint `GET /api/orders/`

    Params `?limit=10&client_id=2&id_order=%204&status=shipped&since=2025-06-05&until=2025-06-07&section=Eletr%C3%B4nica`

    | **Key**   | **Value** | **Discription** |  
    |------------|-----------|------------------|
    |  limit | 10   | Numero máximo de limite |    
    |  client_id | 2   | ID do Cliente  |
    | id_order     | 4   | ID do Pedido |
    | status       |  shipped | pending, confirmed, shipped, delivered, canceled |
    |  since | 2025-06-05   | Data Inicial  |
    | until     | 2025-06-07   | Data Final |
    | section     | Eletrônica   | Eletrodoméstico, Eletrônica, Móveis |
   
    Resposta (200 OK)
    ```
    {
        "total": 1,
        "items": [
            {
            "id": 4,
            "client_id": 2,
            "status": "shipped",
            "total_value": "2890.00",
            "created_at": "2025-06-06T18:48:47.720315"
            }
        ]
    }
    ```

3. Obter pedido por ID:

    Se o pedido não existe, resposta da requisição 403 - Not Found.

    ```
    {
        "detail": "Pedido não encontrado."
    }
    ```

    Endpoint `GET /api/orders/:id/`, order_id = 4

    Resposta (200 OK)
    ```
    {
        "id": 4,
        "client_id": 2,
        "status": "shipped",
        "total_value": "2890.00",
        "items": [
            {
            "id": 5,
            "product_id": 1,
            "quantity": 1,
            "unit_price": "2890.00",
            "total_price": "2890.00"
            }
        ],
        "owner": {
            "name": "Dev User",
            "email": "devu@mail.com",
            "role": "user"
        },
        "created_at": "2025-06-06T18:48:47.720315",
        "updated_at": "2025-06-06T18:48:47.720315"
    }
    
    ```



4. Atualizar um pedido:

    Endpoint: `PUT /api/orders/:id/`, id = 4
    ```
    {
        "client_id": 2,
        "status": "canceled",
        "items": [
            {
            "product_id": 1,
            "quantity": 1
            }
        ]
    }
    ```
    Resposta (200 OK)

    ```
    {
        "id": 4,
        "client_id": 2,
        "status": "canceled",
        "total_value": "2890.00",
        "items": [
            {
            "id": 6,
            "product_id": 1,
            "quantity": 1,
            "unit_price": "2890.00",
            "total_price": "2890.00"
            }
        ],
        "owner": {
            "name": "Dev User",
            "email": "devu@mail.com",
            "role": "user"
        },
        "created_at": "2025-06-06T18:48:47.720315",
        "updated_at": "2025-06-06T19:09:15.839439"
    }    
    ```

5. Deletar um pedido:

    Endpoint: `DELETE /api/orders/:id/`, order_id = 3

    A resposta (204 No Content)


#### 🦫 Dbeaver | 🐘 PostgreSQL

Para visualizar as as tabelas no banco de dados no `PostgreSQL`, poderá usar a ferramenta `DBeaver Communty`, com as seguintes configurações: 

- Host: localhost
- Port: 5432
- Banco de dados: db_smartsales
- Nome de usuário: dev
- Senha: dev_password



#### 🐋 DOCKER

Para facilitar a execução e o desenvolvimento da API REST, utilizamos o Docker para criar um ambiente isolado e consistente. Siga os passos abaixo para colocar a API para rodar em um contêiner:


1. Iniciando os Contêineres:

    ```bash
    docker compose up --build
    ```
2. Aplicando as Migrações:

    Após iniciar os contêineres, execute o seguinte comando para aplicar as migrações do banco de dados PostgreSQL:

    ```bash
    docker compose exec app proetry run alembic upgrade head
    ```
3. Iniciando o Servidor de Desenvolvimento:

    Inicie o servidor de desenvolvimento do Django com o seguinte comando:

    ```bash
    docker compose exec app poetry run 0.0.0.0:8000
    ```
4. Outros Comandos Úteis:
    
    Para rodar o Script:
    ```bash
    docker compose exec app
    ```

    Para iniciar novamente:
    ```bash
    docker compose up -d
    ```
    Iniciar somente o Banco de Dados:

    ```bash
    docker compose up -d db
    ```

    Para poder **Parar** a aplicação no docker basta executar
    ```bash
    docker compose down
    ```

#### 🧪 Teste Unitário 

🚨 Criação ou Manutenção

- Pytest
```python
pytest
```
- Coverage
 1. Executar o comando. 
    ```python
    covarage 
    ```
 2. Executar o comando para gerar o arquivo de cobertura.
    ```python
    covarage html
    ```


## Licença
[MIT License](LICENSE)
