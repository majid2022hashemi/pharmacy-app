# pharmacy_app/backend/app/models/purchase_item.py
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


class PurchaseItem(Base):

    __tablename__ = "purchase_items"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    invoice_id: Mapped[int] = mapped_column(
        ForeignKey("purchase_invoices.id"),
    )

    medicine_id: Mapped[int] = mapped_column(
        ForeignKey("medicines.id"),
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    buy_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    invoice = relationship(
        "PurchaseInvoice",
        back_populates="items",
    )

    medicine = relationship(
        "Medicine",
    )