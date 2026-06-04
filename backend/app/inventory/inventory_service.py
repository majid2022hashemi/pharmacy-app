# backend/app/inventory/inventory_service.py

from sqlalchemy.orm import Session

from app.models import MedicineBatch
from app.exceptions.sale_exceptions import InsufficientStockError


class InventoryService:

    @staticmethod
    def increase_stock(medicine, quantity: int):
        medicine.current_stock += quantity

    @staticmethod
    def decrease_stock(medicine, quantity: int):
        if medicine.current_stock < quantity:
            raise InsufficientStockError(
                f"Not enough stock for {medicine.name}"
            )

        medicine.current_stock -= quantity

    # ✅ FIFO CORE LOGIC
    @staticmethod
    def consume_from_batches(
        db: Session,
        medicine_id: int,
        quantity: int,
    ):
        """
        FIFO consumption from oldest batches (earliest expiry first)
        """

        batches = (
            db.query(MedicineBatch)
            .filter(
                MedicineBatch.medicine_id == medicine_id,
                MedicineBatch.quantity_remaining > 0,
            )
            .order_by(
                MedicineBatch.expiry_date.asc(),
                MedicineBatch.id.asc(),
            )
            .all()
        )

        remaining = quantity

        for batch in batches:

            if remaining <= 0:
                break

            if batch.quantity_remaining >= remaining:
                batch.quantity_remaining -= remaining
                remaining = 0
                break

            else:
                remaining -= batch.quantity_remaining
                batch.quantity_remaining = 0

        if remaining > 0:
            raise InsufficientStockError(
                f"Not enough batch stock for medicine_id={medicine_id}"
            )

        return True