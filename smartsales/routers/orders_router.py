from fastapi import APIRouter, Depends, status

from smartsales.controllers.orders_controller import (
    create_order,
    delete_order,
    list_orders,
    retrieve_order,
    update_order,
)
from smartsales.core.security import get_current_user
from smartsales.schemas.orders_schema import (
    OrderListResponse,
    OrderResponse,
)

router = APIRouter(
    prefix='/orders',
    tags=['Orders'],
    dependencies=[Depends(get_current_user)],
)

router.get(
    '/',
    response_model=OrderListResponse,
    description='List all orders',
)(list_orders)

router.post(
    '/',
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    description='Create new order',
)(create_order)

router.get(
    '/{order_id}',
    response_model=OrderResponse,
    description='Retrieve order',
)(retrieve_order)

router.put(
    '/{order_id}',
    response_model=OrderResponse,
    description='Update order',
)(update_order)

router.delete(
    '/{order_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    description='Delete order',
)(delete_order)
