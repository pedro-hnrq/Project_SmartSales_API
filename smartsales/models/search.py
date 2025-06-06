from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from smartsales.models import table_registry
from smartsales.models.auth import Auth


@table_registry.mapped_as_dataclass
class Search:
    __tablename__ = 'searches'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    query: Mapped[str] = mapped_column(String(255), nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=False)
    owner_id: Mapped[int | None] = mapped_column(
        ForeignKey('auth.id'), nullable=True
    )
    owner: Mapped[Auth | None] = relationship(
        'Auth', init=False, lazy='joined'
    )

    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
