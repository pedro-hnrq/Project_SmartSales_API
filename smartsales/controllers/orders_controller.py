from datetime import datetime
from typing import List, Optional

from fastapi import Depends
from sqlalchemy.orm import Session

from smartsales.core.database import get_session
from smartsales.core.security import get_current_user
from smartsales.schemas.orders_schema import (
    OrderCreate,
    OrderListItem,
    OrderListResponse,
    OrderResponse,
    OrderUpdate,
)
from smartsales.services.orders_service import (
    create_order_service,
    delete_order_service,
    get_order_service,
    list_orders_service,
    update_order_service,
)


async def list_orders(
    limit: int = 10,
    client_id: Optional[int] = None,
    id_order: Optional[int] = None,
    status: Optional[str] = None,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    section: Optional[str] = None,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
) -> OrderListResponse:
    """
    Agora expõe apenas os query‐params: limit, client_id, id_order.
    Internamente, passamos skip=0 e deixamos
    status/date_from/date_to/section como None.
    """
    total, pedidos = list_orders_service(
        db=db,
        current_user=current_user,
        skip=0,  # fixo
        limit=limit,
        client_id=client_id,
        status=status,
        since=since,
        until=until,
        section=section,
        id_order=id_order,
    )

    items: List[OrderListItem] = [OrderListItem.from_orm(o) for o in pedidos]
    return OrderListResponse(total=total, items=items)


async def retrieve_order(
    order_id: int,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
) -> OrderResponse:
    pedido = get_order_service(
        db=db, order_id=order_id, current_user=current_user
    )
    return OrderResponse.from_orm(pedido)


async def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
) -> OrderResponse:
    novo = create_order_service(db=db, data=payload, current_user=current_user)
    return OrderResponse.from_orm(novo)


async def update_order(
    order_id: int,
    payload: OrderUpdate,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
) -> OrderResponse:
    pedido = get_order_service(
        db=db, order_id=order_id, current_user=current_user
    )
    atualizado = update_order_service(
        db=db, order_obj=pedido, data=payload, current_user=current_user
    )
    return OrderResponse.from_orm(atualizado)


async def delete_order(
    order_id: int,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
) -> None:
    pedido = get_order_service(
        db=db, order_id=order_id, current_user=current_user
    )
    delete_order_service(db=db, order_obj=pedido, current_user=current_user)
