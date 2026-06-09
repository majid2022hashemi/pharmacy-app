# pharmacy_app/backend/app/models/sale.py
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Integer,
    String,
    DateTime,
    Numeric,
    func,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database import Base


class Sale(Base):

    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    sale_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    customer_name: Mapped[str | None] = mapped_column(
        String(200)
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=0,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    items = relationship(
        "SaleItem",
        back_populates="sale",
        cascade="all, delete-orphan",
    )