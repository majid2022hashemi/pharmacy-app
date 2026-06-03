
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.sale import SaleCreate, SaleResponse
from app.services.sale_service import SaleService

router = APIRouter()


@router.post("/sales", response_model=SaleResponse)
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):

    return SaleService.create_sale(
        db=db,
        sale_number=sale.sale_number,
        customer_name=sale.customer_name,
        items=sale.items,
    )