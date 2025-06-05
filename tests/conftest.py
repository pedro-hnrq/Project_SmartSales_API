from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from smartsales.core.app import app
from smartsales.core.database import engine, get_session, table_registry


@pytest.fixture(scope='session')
def client():
    """
    Cliente HTTP para testar endpoints
    (leva em conta o app e o banco em memória).
    """
    # Se usar SQLite in-memory para testes:
    table_registry.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    table_registry.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """
    Fornece uma sessão SQLAlchemy
    ligada ao SQLite em memória ou ao banco de testes.
    """
    session = next(get_session())
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def admin_token(client: TestClient):
    """
    Cria um usuário admin e retorna o token JWT para autorizar chamadas.
    """
    # 1) registra admin
    response = client.post(
        '/api/token/register',
        json={
            'name': 'Administrador',
            'email': 'admin@test.com',
            'password': 'Admin123!',
            'role': 'admin',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    # 2) faz login
    response = client.post(
        '/api/token/login',
        json={'email': 'admin@test.com', 'password': 'Admin123!'},
    )
    assert response.status_code == HTTPStatus.OK
    return response.json()['access_token']
