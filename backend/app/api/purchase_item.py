# pharmacy_app/backend/app/api/purchase_item.py
from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import (
    Session,
    joinedload,
)

from app.database import get_db

from app.models import PurchaseItem

from app.schemas.purchase_item import (
    PurchaseItemResponse,
)

router = APIRouter()


@router.get(
    "/purchase-items",
    response_model=list[PurchaseItemResponse],
)
def get_purchase_items(
    db: Session = Depends(get_db),
):

    items = (
        db.query(PurchaseItem)
        .options(
            joinedload(PurchaseItem.medicine)
        )
        .all()
    )

    return items