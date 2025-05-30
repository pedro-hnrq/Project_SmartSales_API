from typing import Optional

from fastapi import Depends
from sqlalchemy.orm import Session

from smartsales.core.database import get_session
from smartsales.core.security import get_current_user
from smartsales.schemas.products_schema import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from smartsales.services.products_service import (
    create_product_service,
    delete_product_service,
    get_product_service,
    get_products_service,
    update_product_service,
)


async def list_products(
    skip: int = 0,
    limit: int = 10,
    section: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    available: Optional[bool] = None,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
) -> ProductListResponse:
    total, items = get_products_service(
        db, current_user, skip, limit, section, price_min, price_max, available
    )
    return ProductListResponse(total=total, items=items)


async def retrieve_product(
    product_id: int,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
) -> ProductResponse:
    p = get_product_service(db, product_id, current_user)
    return ProductResponse.from_orm(p)


async def create_product(
    body: ProductCreate,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
) -> ProductResponse:
    p = create_product_service(db, body, current_user)
    return ProductResponse.from_orm(p)


async def update_product(
    product_id: int,
    body: ProductUpdate,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
) -> ProductResponse:
    p = update_product_service(db, product_id, body, current_user)
    return ProductResponse.from_orm(p)


async def delete_product(
    product_id: int,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
) -> None:
    delete_product_service(db, product_id, current_user)
