from datetime import datetime

from sqlalchemy import (
    Integer,
    ForeignKey,
    DateTime,
    Text,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database import Base


class PurchaseReturn(Base):

    __tablename__ = "purchase_returns"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    purchase_item_id: Mapped[int] = mapped_column(
        ForeignKey("purchase_items.id"),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    purchase_item = relationship(
        "PurchaseItem",
    )