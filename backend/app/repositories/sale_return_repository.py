# backend/app/repositories/sale_return_repository.py

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.sale_return import SaleReturn


class SaleReturnRepository:

    @staticmethod
    def create(
        db: Session,
        sale_item_id: int,
        quantity: int,
        reason: str | None = None,
    ) -> SaleReturn:
        """
        ایجاد رکورد جدید در sale_returns
        """
        obj = SaleReturn(
            sale_item_id=sale_item_id,
            quantity=quantity,
            reason=reason,
        )
        db.add(obj)
        return obj

    @staticmethod
    def get_total_returned(
        db: Session,
        sale_item_id: int,
    ) -> int:
        """
        مجموع تعداد برگشتی یک آیتم فروش
        """
        total = (
            db.query(func.coalesce(func.sum(SaleReturn.quantity), 0))
            .filter(SaleReturn.sale_item_id == sale_item_id)
            .scalar()
        )
        return total