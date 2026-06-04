from decimal import Decimal
from sqlalchemy.orm import Session

from app.models import StockMovement


class StockMovementRepository:

    @staticmethod
    def create(
        db: Session,
        medicine_id: int,
        batch_id: int | None,
        movement_type: str,
        quantity: int,
        unit_price: Decimal | None = None,
        reference_id: int | None = None,
        notes: str | None = None,
    ) -> StockMovement:

        movement = StockMovement(
            medicine_id=medicine_id,
            batch_id=batch_id,
            movement_type=movement_type,
            quantity=quantity,
            unit_price=unit_price,
            reference_id=reference_id,
            notes=notes,
        )

        db.add(movement)

        return movement