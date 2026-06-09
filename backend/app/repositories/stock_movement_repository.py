from app.models import StockMovement

class StockMovementRepository:

    @staticmethod
    def create(
        db,
        medicine_id,
        batch_id,
        movement_type,
        quantity,
        unit_price=None,
        reference_id=None,
        notes=None,
    ):
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
        db.flush()

        print(
            "MOVEMENT CREATED:",
            movement.id,
            movement_type,
            batch_id,
            quantity,
        )

        return movement
    
    
    @staticmethod
    def get_all(db):

        return (
            db.query(StockMovement)
            .order_by(
                StockMovement.created_at.desc()
            )
            .all()
        )