from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    DateTime,
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
    )

    company: Mapped["Company"] = relationship(
        back_populates="purchase_invoices",
    )

    items: Mapped[list["PurchaseItem"]] = relationship(
        back_populates="purchase_invoice",
        cascade="all, delete-orphan",
    )