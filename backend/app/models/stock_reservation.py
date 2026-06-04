from datetime import datetime

from sqlalchemy import (
    Integer,
    ForeignKey,
    DateTime,
    Numeric,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database import Base


class StockReservation(Base):

    __tablename__ = "stock_reservations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    medicine_id: Mapped[int] = mapped_column(
        ForeignKey("medicines.id"),
        nullable=False,
    )

    batch_id: Mapped[int] = mapped_column(
        ForeignKey("medicine_batches.id"),
        nullable=True,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        Integer,
        default="active",  # active | committed | released
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    medicine = relationship("Medicine")
    batch = relationship("MedicineBatch")