from http import HTTPStatus
from typing import List, Optional, Tuple

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from smartsales.models.auth import UserRole
from smartsales.models.products import Product
from smartsales.schemas.products_schema import ProductCreate, ProductUpdate


def get_products_service(
    db: Session,
    current_user,
    skip: int = 0,
    limit: int = 10,
    section: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    available: Optional[bool] = None,
) -> Tuple[int, List[Product]]:
    q = select(Product)
    if current_user.role == UserRole.USER:
        q = q.where(Product.owner_id == current_user.id)
    if section:
        q = q.where(Product.section.ilike(f'%{section}%'))
    if price_min is not None:
        q = q.where(Product.sale_price >= price_min)
    if price_max is not None:
        q = q.where(Product.sale_price <= price_max)
    if available is True:
        q = q.where(Product.stock > 0)
    elif available is False:
        q = q.where(Product.stock == 0)
    all_items = db.execute(q).scalars().all()
    total = len(all_items)
    items = all_items[skip : skip + limit]
    return total, items


def get_product_service(db: Session, product_id: int, current_user) -> Product:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Product not found')
    if (
        current_user.role == UserRole.USER
        and product.owner_id != current_user.id
    ):  # noqa: E501
        raise HTTPException(
            HTTPStatus.FORBIDDEN, 'Not authorized to access this product'
        )
    return product


def create_product_service(
    db: Session, data: ProductCreate, current_user
) -> Product:
    exists = (
        db.query(Product).filter(Product.barcode == data.barcode).first()
        if data.barcode
        else None
    )  # noqa: E501
    if exists:
        raise HTTPException(HTTPStatus.CONFLICT, 'Barcode already exists')
    new_p = Product(
        title=data.title,
        sale_price=data.sale_price,
        section=data.section,
        description=data.description,
        barcode=data.barcode,
        stock=data.stock,
        expiry_date=data.expiry_date,
        images=data.images,
        owner_id=current_user.id,
    )
    db.add(new_p)
    db.commit()
    db.refresh(new_p)
    return new_p


def update_product_service(
    db: Session, product_id: int, data: ProductUpdate, current_user
) -> Product:
    product = get_product_service(db, product_id, current_user)
    for field, value in data.dict(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


def delete_product_service(db: Session, product_id: int, current_user) -> None:
    product = get_product_service(db, product_id, current_user)
    db.delete(product)
    db.commit()
