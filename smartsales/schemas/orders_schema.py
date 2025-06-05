from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, PositiveInt, model_validator


class OrderStatus(str, Enum):
    pending = 'pending'
    confirmed = 'confirmed'
    shipped = 'shipped'
    delivered = 'delivered'
    canceled = 'canceled'


#
# 1. Schemas para os itens do pedido
#
class OrderItemBase(BaseModel):
    product_id: int
    quantity: PositiveInt = Field(..., gt=0)

    @model_validator(mode='after')
    def check_quantity_positive(cls, model):
        return model


class OrderItemCreate(OrderItemBase):
    """Somente product_id e quantity são necessários na criação."""

    pass


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal = Field(..., max_digits=10, decimal_places=2)
    total_price: Decimal = Field(..., max_digits=10, decimal_places=2)

    class Config:
        from_attributes = True


#
# 2. Schemas para criar / atualizar / ler um pedido
#
class OrderCreate(BaseModel):
    client_id: int = Field(..., gt=0)
    status: Optional[OrderStatus] = Field(
        OrderStatus.pending, description='Status inicial do pedido'
    )
    items: List[OrderItemCreate] = Field(
        ..., description='Lista de itens (product_id e quantity) do pedido'
    )

    @model_validator(mode='after')
    def must_have_at_least_one_item(cls, model):
        if not model.items or len(model.items) == 0:
            raise ValueError('Um pedido deve ter pelo menos um item.')
        return model


class OrderUpdate(BaseModel):
    client_id: int = Field(..., gt=0)
    status: Optional[OrderStatus] = Field(
        OrderStatus.pending, description='Status inicial do pedido'
    )
    items: List[OrderItemCreate] = Field(
        ..., description='Lista de itens (product_id e quantity) do pedido'
    )

    @model_validator(mode='after')
    def must_have_at_least_one_item(cls, model):
        if not model.items or len(model.items) == 0:
            raise ValueError('Um pedido deve ter pelo menos um item.')
        return model


class OwnerSchema(BaseModel):
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    client_id: int
    status: OrderStatus
    total_value: Decimal = Field(..., max_digits=10, decimal_places=2)
    items: List[OrderItemResponse]
    owner: OwnerSchema
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


#
# 3. Schemas para listagem (paginação)
#
class OrderListItem(BaseModel):
    id: int
    client_id: int
    status: OrderStatus
    total_value: Decimal = Field(..., max_digits=10, decimal_places=2)
    created_at: datetime

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    total: int
    items: List[OrderListItem]
