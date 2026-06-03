from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database import Base


class Company(Base):

    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=False,
    )

    medicines: Mapped[list["Medicine"]] = relationship(
        back_populates="company",
    )