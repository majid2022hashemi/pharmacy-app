from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app.models.category import Category


from sqlalchemy import (
    Integer,
    String,
    Boolean,
    Numeric,
    DateTime,
    func,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
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

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    generic_name: Mapped[str | None] = mapped_column(
        String(200),
    )

    dosage_form: Mapped[str | None] = mapped_column(
        String(50),
    )

    strength: Mapped[str | None] = mapped_column(
        String(50),
    )

    is_prescription: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    current_stock: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    sale_price: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"),
    )

    category = relationship(
        "Category",
        back_populates="medicines",
    )
    