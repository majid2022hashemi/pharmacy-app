from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.purchase_return import (
    PurchaseReturnCreate,
)

from app.services.purchase_return_service import (
    PurchaseReturnService,
)

router = APIRouter(
    prefix="/purchases",
    tags=["purchase-returns"],
)


@router.post(
    "/{purchase_id}/return"
)
def create_return(
    purchase_id: int,
    data: PurchaseReturnCreate,
    db: Session = Depends(
        get_db
    ),
):

    return (
        PurchaseReturnService
        .return_item(
            db=db,
            purchase_item_id=(
                data.purchase_item_id
            ),
            quantity=data.quantity,
            reason=data.reason,
        )
    )