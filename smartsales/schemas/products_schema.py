from datetime import date
from typing import List, Optional

from fastapi import Form
from pydantic import BaseModel, EmailStr, Field


class ProductBase(BaseModel):
    title: str
    sale_price: float = Field(..., gt=0)
    section: str


class ProductCreate(ProductBase):
    description: Optional[str] = None
    barcode: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0)
    expiry_date: Optional[date] = None
    images: Optional[List[str]] = None

    @classmethod
    def as_form(
        cls,
        title: str = Form(...),
        sale_price: float = Form(..., gt=0),
        section: str = Form(...),
        description: Optional[str] = Form(None),
        barcode: Optional[str] = Form(None),
        stock: Optional[int] = Form(None),
        expiry_date: Optional[date] = Form(None),
    ) -> 'ProductCreate':
        return cls(
            title=title,
            sale_price=sale_price,
            section=section,
            description=description,
            barcode=barcode,
            stock=stock,
            expiry_date=expiry_date,
            images=None,
        )


class ProductUpdate(ProductBase):
    description: Optional[str] = None
    barcode: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0)
    expiry_date: Optional[date] = None
    images: Optional[List[str]] = None

    @classmethod
    def as_form(
        cls,
        title: str = Form(...),
        sale_price: float = Form(..., gt=0),
        section: str = Form(...),
        description: Optional[str] = Form(None),
        barcode: Optional[str] = Form(None),
        stock: Optional[str] = Form(None),
        expiry_date: Optional[date] = Form(None),
    ) -> 'ProductUpdate':
        return cls(
            title=title,
            sale_price=sale_price,
            section=section,
            description=description,
            barcode=barcode,
            stock=int(stock) if stock and stock.isdigit() else None,
            expiry_date=expiry_date,
            images=None,
        )


class OwnerSchema(BaseModel):
    name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True


class ProductResponse(ProductBase):
    id: int
    description: Optional[str]
    barcode: Optional[str]
    stock: Optional[int]
    expiry_date: Optional[date]
    images: Optional[List[str]]
    owner: OwnerSchema

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    total: int
    items: List[ProductResponse]
