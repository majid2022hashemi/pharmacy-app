from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.sale_return import SaleReturnCreate
from app.services.sale_return_service import SaleReturnService
from app.database import get_db

router = APIRouter(
    prefix="/sales",
    tags=["sale-returns"]
)

@router.post("/{sale_id}/return")
def create_return(
    sale_id: int,
    data: SaleReturnCreate,
    db: Session = Depends(get_db),
):
    """
    ثبت برگشت فروش برای یک آیتم
    """
    return SaleReturnService.return_item(
        db=db,
        sale_item_id=data.sale_item_id,
        quantity=data.quantity,
        reason=data.reason,
    )