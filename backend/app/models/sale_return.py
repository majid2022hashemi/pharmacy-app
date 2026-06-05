from datetime import datetime

from sqlalchemy import (
    Integer,
    DateTime,
    ForeignKey,
    String,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database import Base


class SaleReturn(Base):

    __tablename__ = "sale_returns"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    sale_item_id: Mapped[int] = mapped_column(
        ForeignKey("sale_items.id"),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    reason: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    sale_item = relationship(
        "SaleItem",
    )