# backend/app/services/purchase_service.py

from decimal import Decimal

from sqlalchemy.orm import Session

from app.repositories.purchase_repository import (
    PurchaseRepository,
)

from app.repositories.medicine_repository import (
    MedicineRepository,
)

from app.repositories.medicine_batch_repository import (
    MedicineBatchRepository,
)

from app.repositories.stock_movement_repository import (
    StockMovementRepository,
)

from app.inventory.inventory_service import (
    InventoryService,
)

from app.enums.stock_movement_type import (
    StockMovementType,
)

from app.exceptions.purchase_exceptions import (
    MedicineNotFoundError,
)


class PurchaseService:

    @staticmethod
    def create_purchase_invoice(
        db: Session,
        invoice_number: str,
        company_id: int,
        items: list,
    ):

        try:

            invoice = (
                PurchaseRepository.create_invoice(
                    db=db,
                    invoice_number=invoice_number,
                    company_id=company_id,
                )
            )

            total_amount = Decimal("0")

            for item in items:

                medicine = (
                    MedicineRepository.get_by_id(
                        db,
                        item.medicine_id,
                    )
                )

                if medicine is None:

                    raise MedicineNotFoundError(
                        f"Medicine {item.medicine_id} not found"
                    )

                InventoryService.increase_stock(
                    medicine,
                    item.quantity,
                )

                batch = (
                    MedicineBatchRepository.create(
                        db=db,
                        medicine_id=item.medicine_id,
                        batch_number=item.batch_number,
                        expiry_date=item.expiry_date,
                        purchase_price=item.unit_price,
                        sale_price=medicine.sale_price,
                        quantity=item.quantity,
                    )
                )

                PurchaseRepository.create_item(
                    db=db,
                    invoice_id=invoice.id,
                    medicine_id=item.medicine_id,
                    batch_id=batch.id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )

                StockMovementRepository.create(
                    db=db,
                    medicine_id=item.medicine_id,
                    batch_id=batch.id,
                    movement_type=StockMovementType.PURCHASE,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    reference_id=invoice.id,
                    notes=f"Purchase {invoice.invoice_number}",
                )

                total_amount += (
                    item.quantity
                    * item.unit_price
                )

            PurchaseRepository.update_total_amount(
                invoice,
                total_amount,
            )

            db.commit()

            db.refresh(invoice)

            return invoice

        except Exception:

            db.rollback()

            raise