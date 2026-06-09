# backend/app/repositories/purchase_return_repository.py

from sqlalchemy.orm import Session
from app.models import PurchaseReturn


class PurchaseReturnRepository:

    @staticmethod
    def create(
        db: Session,
        purchase_item_id: int,
        quantity: int,
        reason: str | None = None,
    ) -> PurchaseReturn:
        """
        ایجاد رکورد برگشت خرید جدید
        """
        purchase_return = PurchaseReturn(
            purchase_item_id=purchase_item_id,
            quantity=quantity,
            reason=reason,
        )
        db.add(purchase_return)
        db.flush()  # آماده‌سازی id
        return purchase_return

    @staticmethod
    def get_total_returned(
        db: Session,
        purchase_item_id: int,
    ) -> int:
        """
        محاسبه کل تعداد برگشت داده شده برای یک آیتم خرید
        """
        total = (
            db.query(PurchaseReturn)
            .filter(PurchaseReturn.purchase_item_id == purchase_item_id)
            .with_entities(
                PurchaseReturn.quantity
            )
            .all()
        )
        return sum(q[0] for q in total) if total else 0

    @staticmethod
    def get_by_id(
        db: Session,
        return_id: int,
    ) -> PurchaseReturn | None:
        """
        دریافت یک رکورد برگشت خرید بر اساس شناسه
        """
        return db.query(PurchaseReturn).filter(PurchaseReturn.id == return_id).first()

    @staticmethod
    def get_all_for_item(
        db: Session,
        purchase_item_id: int,
    ) -> list[PurchaseReturn]:
        """
        دریافت همه رکوردهای برگشت برای یک آیتم خرید مشخص
        """
        return (
            db.query(PurchaseReturn)
            .filter(PurchaseReturn.purchase_item_id == purchase_item_id)
            .order_by(PurchaseReturn.id.asc())
            .all()
        )