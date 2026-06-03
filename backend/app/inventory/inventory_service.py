# backend/app/inventory/inventory_service.py

from app.models import Medicine

from app.exceptions.sale_exceptions import (
    InsufficientStockError,
)


class InventoryService:

    @staticmethod
    def increase_stock(
        medicine: Medicine,
        quantity: int,
    ):

        medicine.current_stock += quantity

    @staticmethod
    def decrease_stock(
        medicine: Medicine,
        quantity: int,
    ):

        if medicine.current_stock < quantity:

            raise InsufficientStockError(
                f"Not enough stock for {medicine.name}"
            )

        medicine.current_stock -= quantity