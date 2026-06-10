# pharmacy_app/backend/app/models/medicine.py

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Integer,
    String,
    Boolean,
    Numeric,
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


class Medicine(Base):

    __tablename__ = "medicines"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
    )

    virtual_code: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    trade_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    generic_name: Mapped[str | None] = mapped_column(
        String(200)
    )

    dosage_form: Mapped[str | None] = mapped_column(
        String(50)
    )

    strength: Mapped[str | None] = mapped_column(
        String(50)
    )

    is_prescription: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    default_quantity: Mapped[int] = mapped_column(
        Integer,
        default=1,
    )

    current_stock: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    sale_price: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False,
    )

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"),
        nullable=False,
    )

    category: Mapped["Category"] = relationship(
        back_populates="medicines",
    )

    company: Mapped["Company"] = relationship(
        back_populates="medicines",
    )

    purchase_items: Mapped[list["PurchaseItem"]] = relationship(
        "PurchaseItem",
        back_populates="medicine",
    )

    sale_items: Mapped[list["SaleItem"]] = relationship(
        "SaleItem",
        back_populates="medicine",
    )

    batches: Mapped[list["MedicineBatch"]] = relationship(
        "MedicineBatch",
        back_populates="medicine",
        cascade="all, delete-orphan",
    )