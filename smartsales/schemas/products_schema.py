from datetime import date, datetime
from typing import List, Optional

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


class ProductUpdate(BaseModel):
    title: Optional[str]
    sale_price: Optional[float] = Field(None, gt=0)
    section: Optional[str]
    description: Optional[str]
    barcode: Optional[str]
    stock: Optional[int] = Field(None, ge=0)
    expiry_date: Optional[date]
    images: Optional[List[str]]


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
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    total: int
    items: List[ProductResponse]
