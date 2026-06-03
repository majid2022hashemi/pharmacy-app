# backend/app/services/sale_service.py

from decimal import Decimal

from sqlalchemy.orm import Session

from app.repositories.sale_repository import (
    SaleRepository,
)

from app.repositories.medicine_repository import (
    MedicineRepository,
)

from app.inventory.inventory_service import (
    InventoryService,
)

from app.exceptions.sale_exceptions import (
    MedicineNotFoundError,
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

                InventoryService.decrease_stock(
                    medicine,
                    item.quantity,
                )

                SaleRepository.create_item(
                    db=db,
                    sale_id=sale.id,
                    medicine_id=item.medicine_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )

                total_amount += (
                    item.quantity
                    * item.unit_price
                )

            sale.total_amount = total_amount

            db.commit()

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
    