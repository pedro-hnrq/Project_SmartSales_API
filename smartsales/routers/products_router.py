from fastapi import APIRouter, Depends, status

from smartsales.controllers.products_controller import (
    create_product,
    delete_product,
    list_products,
    retrieve_product,
    update_product,
)
from smartsales.core.security import get_current_user
from smartsales.schemas.products_schema import (
    ProductListResponse,
    ProductResponse,
)

router = APIRouter(
    prefix='/products',
    tags=['Products'],
    dependencies=[Depends(get_current_user)],
)

router.get(
    '/', response_model=ProductListResponse, description='List all products'
)(list_products)

router.post(
    '/',
    response_model=ProductResponse,
    description='Create new products',
    status_code=status.HTTP_201_CREATED,
)(create_product)

router.get(
    '/{product_id}',
    response_model=ProductResponse,
    description='Retrieve products',
)(retrieve_product)

router.put(
    '/{product_id}',
    response_model=ProductResponse,
    description='Update products',
)(update_product)

router.delete(
    '/{product_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    description='Deçete products',
)(delete_product)
