# pharmacy_app/backend/app/schemas/purchase_invoice_create.py

from datetime import date
from decimal import Decimal
from typing import List

from pydantic import BaseModel, Field


class PurchaseInvoiceItemCreate(BaseModel):

    medicine_id: int

    quantity: int = Field(gt=0)

    unit_price: Decimal = Field(gt=0)

    batch_number: str

    expiry_date: date


class PurchaseInvoiceCreate(BaseModel):

    invoice_number: str

    company_id: int

    items: List[PurchaseInvoiceItemCreate]