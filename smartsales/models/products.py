from datetime import date, datetime

from sqlalchemy import DECIMAL, JSON, Date, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from smartsales.models import table_registry
from smartsales.models.auth import Auth


@table_registry.mapped_as_dataclass
class Product:
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    sale_price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    section: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    barcode: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    stock: Mapped[int] = mapped_column(Integer, nullable=True)
    expiry_date: Mapped[date] = mapped_column(Date, nullable=True)
    images: Mapped[list[str]] = mapped_column(JSON, nullable=True)
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
