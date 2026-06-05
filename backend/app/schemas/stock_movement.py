from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class StockMovementRead(BaseModel):

    id: int

    medicine_id: int

    batch_id: int | None

    movement_type: str

    quantity: int

    unit_price: Decimal | None

    reference_id: int | None

    notes: str | None

    created_at: datetime

    class Config:
        from_attributes = True