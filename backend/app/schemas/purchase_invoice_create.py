# pharmacy_app/backend/app/schemas/purchase_invoice_create.py

from decimal import Decimal
from typing import List

from pydantic import BaseModel, Field


class PurchaseInvoiceItemCreate(BaseModel):
    medicine_id: int
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(gt=0)


class PurchaseInvoiceCreate(BaseModel):
    invoice_number: str
    company_id: int
    items: List[PurchaseInvoiceItemCreate]