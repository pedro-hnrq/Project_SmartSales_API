from datetime import datetime
from enum import Enum

from sqlalchemy import (
    DECIMAL,
    ForeignKey,
    Integer,
    func,
)
from sqlalchemy import (
    Enum as SqlEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from smartsales.models import table_registry
from smartsales.models.auth import Auth
from smartsales.models.clients import Client
from smartsales.models.products import Product


class OrderStatus(str, Enum):
    pending = 'pending'
    confirmed = 'confirmed'
    shipped = 'shipped'
    delivered = 'delivered'
    canceled = 'canceled'


@table_registry.mapped_as_dataclass
class Order:
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    client_id: Mapped[int] = mapped_column(
        ForeignKey('clients.id'), nullable=False
    )
    client: Mapped[Client] = relationship('Client', init=False, lazy='joined')

    total_value: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        SqlEnum(OrderStatus), nullable=False
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey('auth.id'), nullable=False
    )
    owner: Mapped[Auth] = relationship('Auth', init=False, lazy='joined')

    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )

    # relacionamento com itens
    items: Mapped[list['OrderItem']] = relationship(
        'OrderItem',
        back_populates='order',
        cascade='all, delete-orphan',
        init=False,
        lazy='joined',
    )


@table_registry.mapped_as_dataclass
class OrderItem:
    __tablename__ = 'order_items'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    order_id: Mapped[int] = mapped_column(
        ForeignKey('orders.id', ondelete='CASCADE'), nullable=False
    )
    order: Mapped[Order] = relationship(
        'Order', init=False, back_populates='items'
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey('products.id'), nullable=False
    )
    product: Mapped[Product] = relationship(
        'Product', init=False, lazy='joined'
    )

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    total_price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
