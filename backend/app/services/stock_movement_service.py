from app.repositories.stock_movement_repository import (
    StockMovementRepository,
)


class StockMovementService:

    @staticmethod
    def get_movements(db):

        return (
            StockMovementRepository.get_all(
                db
            )
        )