# backend/app/models/purchase_invoice.py

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Integer,
    String,
    DateTime,
    Numeric,
    ForeignKey,
    func,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database import Base


class PurchaseInvoice(Base):

    __tablename__ = "purchase_invoices"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    invoice_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    purchase_date: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"),
        nullable=False,
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=0,
    )

    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="purchase_invoices",
    )

    items: Mapped[list["PurchaseItem"]] = relationship(
        "PurchaseItem",
        back_populates="purchase_invoice",
        cascade="all, delete-orphan",
    )