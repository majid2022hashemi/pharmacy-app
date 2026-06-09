# pharmacy_app/backend/app/models/sale_item.py

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import (
    Integer,
    Numeric,
    ForeignKey,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database import Base


class SaleItem(Base):

    __tablename__ = "sale_items"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    sale_id: Mapped[int] = mapped_column(
        ForeignKey("sales.id"),
        nullable=False,
    )

    medicine_id: Mapped[int] = mapped_column(
        ForeignKey("medicines.id"),
        nullable=False,
    )

    batch_id: Mapped[int | None] = mapped_column(
        ForeignKey("medicine_batches.id"),
        nullable=True,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    sale = relationship(
        "Sale",
        back_populates="items",
    )

    medicine = relationship(
        "Medicine",
        back_populates="sale_items",
    )

    batch = relationship(
        "MedicineBatch",
    )