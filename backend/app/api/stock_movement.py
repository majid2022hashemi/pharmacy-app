from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database import get_db

from app.services.stock_movement_service import (
    StockMovementService,
)

from app.schemas.stock_movement import (
    StockMovementRead,
)

router = APIRouter(
    prefix="/stock-movements",
    tags=["Stock Movements"],
)


@router.get(
    "/",
    response_model=list[StockMovementRead],
)
def get_movements(
    db: Session = Depends(get_db),
):

    return (
        StockMovementService.get_movements(
            db
        )
    )