from typing import List, Optional

from fastapi import Depends, File, UploadFile
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
    body: ProductCreate = Depends(ProductCreate.as_form),
    images: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
) -> ProductResponse:
    # 1) Salvar os arquivos físicos (se houver)
    image_paths: List[str] = []
    if images:
        for img in images:
            file_location = f'smartsales/static/uploads/{img.filename}'
            with open(file_location, 'wb+') as f:
                f.write(img.file.read())
            image_paths.append(file_location)

    # 2) “injetar” os paths no objeto ProductCreate
    body.images = image_paths

    # 3) Chamar o service passando o ProductCreate (que já tem body.images)
    p = create_product_service(db, body, current_user)
    return ProductResponse.from_orm(p)


async def update_product(
    product_id: int,
    body: ProductUpdate = Depends(ProductUpdate.as_form),
    images: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
) -> ProductResponse:
    if images:
        image_paths: List[str] = []
        for img in images:
            file_location = f'smartsales/static/uploads/{img.filename}'
            with open(file_location, 'wb+') as f:
                f.write(img.file.read())
            image_paths.append(file_location)
        body.images = image_paths  # sobrescreve as imagens

    p = update_product_service(db, product_id, body, current_user)
    return ProductResponse.from_orm(p)


async def delete_product(
    product_id: int,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
) -> None:
    delete_product_service(db, product_id, current_user)
