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
    PurchaseItemCreate,
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


@router.post(
    "/purchase-items",
    response_model=PurchaseItemResponse,
)
def create_purchase_item(
    item: PurchaseItemCreate,
    db: Session = Depends(get_db),
):

    purchase_item = PurchaseItem(
        purchase_invoice_id=item.purchase_invoice_id,
        medicine_id=item.medicine_id,
        quantity=item.quantity,
        unit_price=item.unit_price,
    )

    db.add(purchase_item)
    db.commit()
    db.refresh(purchase_item)

    return purchase_item