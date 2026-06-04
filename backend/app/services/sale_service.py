# backend/app/services/sale_service.py

from decimal import Decimal

from sqlalchemy.orm import Session

from app.repositories.sale_repository import (
    SaleRepository,
)

from app.repositories.medicine_repository import (
    MedicineRepository,
)

from app.repositories.medicine_batch_repository import (
    MedicineBatchRepository,
)

from app.exceptions.sale_exceptions import (
    MedicineNotFoundError,
    InsufficientStockError,
)

from app.schemas.sale import (
    SaleItemCreate,
)


class SaleService:

    @staticmethod
    def create_sale(
        db: Session,
        sale_number: str,
        customer_name: str | None,
        items: list[SaleItemCreate],
    ):

        try:

            sale = SaleRepository.create_sale(
                db=db,
                sale_number=sale_number,
                customer_name=customer_name,
            )

            total_amount = Decimal("0")

            for item in items:

                medicine = MedicineRepository.get_by_id(
                    db,
                    item.medicine_id,
                )

                if medicine is None:

                    raise MedicineNotFoundError(
                        f"Medicine {item.medicine_id} not found"
                    )

                remaining_quantity = item.quantity

                batches = (
                    MedicineBatchRepository
                    .get_available_batches(
                        db,
                        item.medicine_id,
                    )
                )

                total_available = sum(
                    batch.quantity_remaining
                    for batch in batches
                )

                if total_available < item.quantity:

                    raise InsufficientStockError(
                        f"Not enough stock for {medicine.name}"
                    )

                for batch in batches:

                    if remaining_quantity <= 0:
                        break

                    sell_quantity = min(
                        remaining_quantity,
                        batch.quantity_remaining,
                    )

                    batch.quantity_remaining -= sell_quantity

                    SaleRepository.create_item(
                        db=db,
                        sale_id=sale.id,
                        medicine_id=item.medicine_id,
                        batch_id=batch.id,
                        quantity=sell_quantity,
                        unit_price=item.unit_price,
                    )

                    remaining_quantity -= sell_quantity

                medicine.current_stock -= item.quantity

                total_amount += (
                    item.quantity
                    * item.unit_price
                )

            sale.total_amount = total_amount

            db.commit()

            db.refresh(sale)

            return SaleRepository.get_by_id(
                db,
                sale.id,
            )

        except Exception:

            db.rollback()

            raise

    @staticmethod
    def get_sale(
        db: Session,
        sale_id: int,
    ):

        return SaleRepository.get_by_id(
            db,
            sale_id,
        )

    @staticmethod
    def get_sales(
        db: Session,
    ):

        return SaleRepository.get_all(
            db,
        )