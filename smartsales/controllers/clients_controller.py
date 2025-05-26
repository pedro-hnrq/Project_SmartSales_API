from typing import Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from smartsales.core.database import get_session
from smartsales.core.security import get_current_user
from smartsales.schemas.clients_schema import (
    ClientCreate,
    ClientListResponse,
    ClientResponse,
    ClientUpdate,
)
from smartsales.services.clients_service import (
    create_client_service,
    delete_client_service,
    get_client_service,
    get_clients_service,
    update_client_service,
)

router_auth = OAuth2PasswordBearer(tokenUrl='/token/login')


async def list_clients(
    skip: int = 0,
    limit: int = 10,
    name: Optional[str] = None,
    email: Optional[str] = None,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
) -> ClientListResponse:
    total, items = get_clients_service(
        db, current_user, skip, limit, name, email
    )
    return ClientListResponse(total=total, items=items)


async def retrieve_client(
    id: int,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
) -> ClientResponse:
    client = get_client_service(db, id, current_user)
    return ClientResponse.from_orm(client)


async def create_client_controller(
    body: ClientCreate,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
) -> ClientResponse:
    client = create_client_service(db, body, current_user)
    return ClientResponse.from_orm(client)


async def update_client_controller(
    id: int,
    body: ClientUpdate,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
) -> ClientResponse:
    client = update_client_service(db, id, body, current_user)
    return ClientResponse.from_orm(client)


async def delete_client_controller(
    id: int,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
) -> None:
    delete_client_service(db, id, current_user)
