from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Medicine(Base):

    __tablename__ = "medicines"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )