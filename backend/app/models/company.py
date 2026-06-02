# pharmacy_app/backend/app/models/company.py
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

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


# class Company(Base):

#     __tablename__ = "companies"

#     id: Mapped[int] = mapped_column(
#         Integer,
#         primary_key=True,
#     )

#     name: Mapped[str] = mapped_column(
#         String(200),
#         unique=True,
#         nullable=False,
#     )

#     medicines = relationship(
#         "Medicine",
#         back_populates="company",
#     )