# pharmacy_app/backend/app/schemas/purchase_invoice_create.py

from decimal import Decimal

from pydantic import BaseModel


class PurchaseInvoiceItemCreate(BaseModel):

    medicine_id: int
    quantity: int
    unit_price: Decimal


class PurchaseInvoiceCreate(BaseModel):

    invoice_number: str
    company_id: int

    items: list[PurchaseInvoiceItemCreate]