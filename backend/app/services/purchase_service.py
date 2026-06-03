# pharmacy_app/backend/app/services/purchase_service.py

from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import Medicine

from app.repositories.purchase_repository import (
    PurchaseRepository,
)

from app.repositories.medicine_repository import (
    MedicineRepository,
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

            total = Decimal("0")

            for item in items:

                medicine = (
                    MedicineRepository.get_by_id(
                        db,
                        item.medicine_id,
                    )
                )

                if medicine is None:
                    raise MedicineNotFoundError()

                medicine.current_stock += item.quantity

                PurchaseRepository.create_item(
                    db=db,
                    invoice_id=invoice.id,
                    medicine_id=item.medicine_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )

                total += (
                    item.quantity *
                    item.unit_price
                )

            PurchaseRepository.update_total_amount(
                invoice,
                total,
            )

            db.commit()

            db.refresh(invoice)

            return invoice

        except Exception:
            db.rollback()
            raise