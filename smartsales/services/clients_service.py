from http import HTTPStatus
from typing import Optional, Tuple

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from smartsales.models.auth import UserRole
from smartsales.models.clients import Client
from smartsales.schemas.clients_schema import ClientCreate, ClientUpdate


def get_clients_service(
    db: Session,
    current_user,
    skip: int = 0,
    limit: int = 10,
    name: Optional[str] = None,
    email: Optional[str] = None,
) -> Tuple[int, list[Client]]:
    query = select(Client)
    # filtro por role
    if current_user.role == UserRole.USER:
        query = query.where(Client.owner_id == current_user.id)
    # filtros adicionais
    if name:
        query = query.where(Client.name.ilike(f'%{name}%'))
    if email:
        query = query.where(Client.email == email)
    total_query = query.with_only_columns(func.count()).order_by(None)
    total = db.execute(total_query).scalar()
    results = db.execute(query.offset(skip).limit(limit)).scalars().all()
    return total, results


def get_client_service(db: Session, client_id: int, current_user) -> Client:
    client = db.get(Client, client_id)
    if not client:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Client not found')
    if (
        current_user.role == UserRole.USER
        and client.owner_id != current_user.id
    ):  # noqa: E501
        raise HTTPException(
            HTTPStatus.FORBIDDEN, 'Not authorized to access this client'
        )
    return client


def create_client_service(
    db: Session, data: ClientCreate, current_user
) -> Client:
    stmt = select(Client).where(
        (Client.email == data.email) | (Client.cpf == data.cpf)
    )
    exists = db.execute(stmt).first()
    if exists:
        raise HTTPException(HTTPStatus.CONFLICT, 'Email or CPF already exists')
    new_client = Client(
        name=data.name,
        email=data.email,
        cpf=data.cpf,
        owner_id=current_user.id,
    )
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return new_client


def update_client_service(
    db: Session, client_id: int, data: ClientUpdate, current_user
) -> Client:
    client = get_client_service(db, client_id, current_user)
    for field, value in data.dict(exclude_unset=True).items():
        setattr(client, field, value)
    db.commit()
    db.refresh(client)
    return client


def delete_client_service(db: Session, client_id: int, current_user) -> None:
    client = get_client_service(db, client_id, current_user)
    db.delete(client)
    db.commit()
