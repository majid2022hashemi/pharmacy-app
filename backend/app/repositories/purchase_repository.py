# pharmacy_app/backend/app/repositories/purchase_repository.py

from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import (
    PurchaseInvoice,
    PurchaseItem,
)


class PurchaseRepository:

    @staticmethod
    def create_invoice(
        db: Session,
        invoice_number: str,
        company_id: int,
    ) -> PurchaseInvoice:

        invoice = PurchaseInvoice(
            invoice_number=invoice_number,
            company_id=company_id,
            total_amount=Decimal("0"),
        )

        db.add(invoice)

        db.flush()

        return invoice

    @staticmethod
    def create_item(
        db: Session,
        invoice_id: int,
        medicine_id: int,
        batch_id: int,
        quantity: int,
        unit_price: Decimal,
    ) -> PurchaseItem:

        item = PurchaseItem(
            purchase_invoice_id=invoice_id,
            medicine_id=medicine_id,
            batch_id=batch_id,
            quantity=quantity,
            unit_price=unit_price,
        )

        db.add(item)

        return item

    @staticmethod
    def update_total_amount(
        invoice: PurchaseInvoice,
        total_amount: Decimal,
    ):
        invoice.total_amount = total_amount

    # -----------------------
    # متد اضافه شده برای گرفتن آیتم خرید
    # -----------------------
    @staticmethod
    def get_purchase_item(
        db: Session,
        purchase_item_id: int,
    ) -> PurchaseItem | None:
        return (
            db.query(PurchaseItem)
            .filter(PurchaseItem.id == purchase_item_id)
            .first()
        )