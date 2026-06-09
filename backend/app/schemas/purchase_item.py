# pharmacy_app/backend/app/schemas/purchase_item.py

from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from app.schemas.medicine import (
    MedicineResponse,
)


class PurchaseItemCreate(BaseModel):

    purchase_invoice_id: int

    medicine_id: int

    quantity: int

    unit_price: Decimal

    batch_number: str

    expiry_date: date


class PurchaseItemResponse(BaseModel):

    id: int

    purchase_invoice_id: int

    medicine_id: int

    quantity: int

    unit_price: Decimal

    medicine: MedicineResponse

    class Config:
        from_attributes = True