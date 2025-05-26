from datetime import datetime

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from smartsales.models import table_registry
from smartsales.models.auth import Auth


@table_registry.mapped_as_dataclass
class Client:
    __tablename__ = 'clients'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    cpf: Mapped[str] = mapped_column(String, unique=True, nullable=False)

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
