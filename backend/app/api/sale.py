# pharmacy_app/backend/app/api/sale.py

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.sale import (
    SaleCreate,
    SaleResponse,
)

from sqlalchemy.exc import IntegrityError
from app.services.sale_service import SaleService
from app.exceptions.sale_exceptions import InsufficientStockError, MedicineNotFoundError

router = APIRouter()


@router.post("/sales", response_model=SaleResponse)
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    try:
        return SaleService.create_sale(
            db=db,
            sale_number=sale.sale_number,
            customer_name=sale.customer_name,
            items=sale.items,
        )
    except InsufficientStockError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except MedicineNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="شماره سند تکراری است")


@router.get(
    "/sales",
    response_model=list[SaleResponse],
)
def get_sales(
    db: Session = Depends(get_db),
):

    return SaleService.get_sales(db)


@router.get(
    "/sales/{sale_id}",
    response_model=SaleResponse,
)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
):

    sale = SaleService.get_sale(
        db,
        sale_id,
    )

    if sale is None:

        raise HTTPException(
            status_code=404,
            detail="Sale not found",
        )

    return sale