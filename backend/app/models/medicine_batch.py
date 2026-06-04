# backend/app/models/medicine_batch.py
from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import (
    Integer,
    String,
    Date,
    Numeric,
    ForeignKey,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database import Base


class MedicineBatch(Base):

    __tablename__ = "medicine_batches"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    medicine_id: Mapped[int] = mapped_column(
        ForeignKey("medicines.id"),
        nullable=False,
    )

    batch_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    expiry_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    purchase_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    sale_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    quantity_received: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    quantity_remaining: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    medicine: Mapped["Medicine"] = relationship(
        "Medicine",
        back_populates="batches",
    )