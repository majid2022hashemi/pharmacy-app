# backend/app/services/sale_return_service.py

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.sale_repository import SaleRepository
from app.repositories.sale_return_repository import SaleReturnRepository
from app.repositories.stock_movement_repository import StockMovementRepository
from app.enums.stock_movement_type import StockMovementType


class SaleReturnService:

    @staticmethod
    def return_item(
        db: Session,
        sale_item_id: int,
        quantity: int,
        reason: str | None = None,
    ):
        """
        پردازش برگشت یک آیتم فروش
        - بررسی موجود بودن آیتم فروش
        - اعتبارسنجی مقدار برگشت
        - آپدیت موجودی medicine و batch
        - ثبت در جدول sale_returns و stock_movements
        """

        # اعتبارسنجی اولیه مقدار
        if quantity <= 0:
            raise HTTPException(
                status_code=400,
                detail="Quantity must be greater than zero",
            )

        try:
            # گرفتن آیتم فروش
            sale_item = SaleRepository.get_sale_item(db, sale_item_id)
            if sale_item is None:
                raise HTTPException(
                    status_code=404,
                    detail="Sale item not found",
                )

            # محاسبه مجموع برگشت‌های قبلی
            returned_qty = SaleReturnRepository.get_total_returned(db, sale_item_id)
            available_to_return = sale_item.quantity - returned_qty

            if quantity > available_to_return:
                raise HTTPException(
                    status_code=400,
                    detail=f"Only {available_to_return} items can be returned"
                )

            # آپدیت موجودی medicine و batch
            medicine = sale_item.medicine
            batch = sale_item.batch

            if batch is None:
                raise HTTPException(
                    status_code=500,
                    detail="Sale item has no batch assigned"
                )

            batch.quantity_remaining += quantity
            medicine.current_stock += quantity

            # ثبت برگشت در جدول sale_returns
            SaleReturnRepository.create(
                db=db,
                sale_item_id=sale_item_id,
                quantity=quantity,
                reason=reason,
            )

            # ثبت حرکت انبار در جدول stock_movements
            StockMovementRepository.create(
                db=db,
                medicine_id=medicine.id,
                batch_id=batch.id,
                movement_type=StockMovementType.SALE_RETURN,
                quantity=quantity,
                unit_price=sale_item.unit_price,
                reference_id=sale_item.sale_id,
                notes="Sale Return",
            )

            # Commit تراکنش
            db.commit()

            return {"message": "returned"}

        except HTTPException:
            db.rollback()
            raise

        except Exception as e:
            db.rollback()
            print(f"Error in return_item: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error",
            )