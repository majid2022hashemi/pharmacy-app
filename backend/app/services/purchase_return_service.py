from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.purchase_repository import (
    PurchaseRepository,
)

from app.repositories.purchase_return_repository import (
    PurchaseReturnRepository,
)

from app.repositories.stock_movement_repository import (
    StockMovementRepository,
)

from app.enums.stock_movement_type import (
    StockMovementType,
)


class PurchaseReturnService:

    @staticmethod
    def return_item(
        db: Session,
        purchase_item_id: int,
        quantity: int,
        reason: str | None = None,
    ):

        if quantity <= 0:
            raise HTTPException(
                status_code=400,
                detail="Quantity must be greater than zero",
            )

        try:

            purchase_item = (
                PurchaseRepository
                .get_purchase_item(
                    db,
                    purchase_item_id,
                )
            )

            if purchase_item is None:
                raise HTTPException(
                    status_code=404,
                    detail="Purchase item not found",
                )

            returned_qty = (
                PurchaseReturnRepository
                .get_total_returned(
                    db,
                    purchase_item_id,
                )
            )

            available_to_return = (
                purchase_item.quantity
                - returned_qty
            )

            if quantity > available_to_return:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Only {available_to_return} "
                        f"items can be returned"
                    ),
                )

            medicine = purchase_item.medicine

            batch = purchase_item.batch

            if batch is None:
                raise HTTPException(
                    status_code=400,
                    detail="Purchase item batch not found",
                )

            if batch.quantity_remaining < quantity:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Batch only contains "
                        f"{batch.quantity_remaining}"
                    ),
                )

            batch.quantity_remaining -= quantity

            medicine.current_stock -= quantity

            PurchaseReturnRepository.create(
                db=db,
                purchase_item_id=purchase_item_id,
                quantity=quantity,
                reason=reason,
            )

            StockMovementRepository.create(
                db=db,
                medicine_id=medicine.id,
                batch_id=batch.id,
                movement_type=(
                    StockMovementType
                    .PURCHASE_RETURN
                ),
                quantity=quantity,
                unit_price=(
                    purchase_item.unit_price
                ),
                reference_id=(
                    purchase_item.purchase_invoice_id
                ),
                notes="Purchase Return",
            )

            db.commit()

            return {
                "message": "returned"
            }

        except HTTPException:
            db.rollback()
            raise

        except Exception as e:

            db.rollback()

            print(
                "PURCHASE RETURN ERROR:",
                repr(e)
            )

            raise HTTPException(
                status_code=500,
                detail=str(e),
            )