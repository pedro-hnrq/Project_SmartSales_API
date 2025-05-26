# Project_SmartSales_API

#### 💻 Pré-requisitos

Antes de começar, verifique se você atendeu aos seguintes requisitos:

- Python 
- FastAPI
- Poetry
- GIT 
- PostgreSQL
- Docker
- Docker Compose
- Postman (opcional)


#### 🛠️ Instalação

Faça o clone do projeto:
```bash
git clone git@github.com:pedro-hnrq/Project_SmartSales.git
```

Após clonar o repositório acesse o diretório:
```bash
cd Project_SmartSales_API
``` 

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

Tasks - Atalho que poderá utilizar no terminal.

 | **Descrição**   | **Comando** | 
|------------|-----------|
| Linter        |  ```task lint ``` | 
|  Pré Formato | ```task pre_format ```   | 
| Formato     | ```task format ```   | 
| Execução do Projeto       |  ```task run ``` | 
|  Pre Teste | ```task pre_test ```   | 
| Teste     | ```task test ```  | 
| Coverage     | ```task post_test ```  | 

🧪 Teste Unitário 

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

#### 🗺️ APIs


🔐 **Autenticação** - JWT
 
 Antes de começarmos a interagir com a API, precisamos obter um token de acesso JWT (JSON Web Token). Esse token é como uma chave que garante que você tenha permissão para acessar os recursos protegidos da API.

 | **Método**   | **Endpoint** | **Descrição** |  **Autenticação** |
|------------|-----------|------------------|------------------|
| POST       |  `/api/token/login` | Realizar login   |  NÃO  |
|  POST | `/api/token/register/`   | Registar na plataforma   |  NÃO |
| POST     | `/api/token/refresh-token/`   | Obter access_token |  NÃO |

 Existem duas tipos de Role: _administrador_ e _usuário regular_, denominado de admin e user. Dessa forma, o _administrador_, terá acesso a todos os endpoints e, já _usuário regular_ terá acesso somente o endpoint que relacionado ao seu usuário.

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


🛗 **Clientes**

 | **Método**   | **Endpoint** | **Descrição** |  **Autenticação** |
|------------|-----------|------------------|------------------|
| GET       |  `/api/clients/` | Listar somente a clientes    |  SIM  |
|  GET | `/api/clients/:id/`   | Obter com ID a clientes   |  SIM |
| POST     | `/api/clients/`   | Criar novo clientes |  SIM |
|  PUT | `/api/clients/:id/`   | Atualizar registro de clientes   | SIM  |
| DELETE     | `/api/clients/:id/`   | Deleta registro do clientes | SIM  |

1. Criar um cliente:

    Endpoint: `POST /api/clients/`


#### 🦫 Dbeaver | 🐘 PostgreSQL

Para visualizar as as tabelas no banco de dados no `PostgreSQL`, poderá usar a ferramenta `DBeaver Communty`, com as seguintes configurações: 

- Host: localhost
- Port: 5432
- Banco de dados: db_smartsales
- Nome de usuário: dev
- Senha: dev_password



#### 🐋 DOCKER

Para facilitar a execução e o desenvolvimento da API REST, utilizamos o Docker para criar um ambiente isolado e consistente. Siga os passos abaixo para colocar a API para rodar em um contêiner:

1. Configurando o `.env`:

    Altere a variável `POSTGRES_HOST` de `localhost` para `db`.

2. Iniciando os Contêineres:

    ```bash
    docker compose up --build
    ```
3. Aplicando as Migrações:

    Após iniciar os contêineres, execute o seguinte comando para aplicar as migrações do banco de dados PostgreSQL:

    ```bash
    docker compose exec app python manage.py migrate
    ```
4. Criando um Superusuário:
    
    Para acessar o painel administrativo do Django, crie um superusuário com o seguinte comando:
    ```bash
    docker compose exec app python manage.py createsuperuser
    ```

5. Iniciando o Servidor de Desenvolvimento:

    Inicie o servidor de desenvolvimento do Django com o seguinte comando:

    ```bash
    docker compose exec app python manage.py runserver 0.0.0.0:8000
    ```

6. Outros Comandos Úteis:
    
    Para rodar o Script:
    ```bash
    docker compose exec app python manage.py populate_db
    ```

    Para iniciar o Celery:
    ```bash
    docker compose exec app celery -A core worker -l INFO
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
