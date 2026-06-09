# backend/app/schemas/purchase_invoice.py

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.schemas.company import CompanyResponse
from app.schemas.purchase_item import PurchaseItemResponse


class PurchaseInvoiceResponse(BaseModel):

    id: int

    invoice_number: str

    purchase_date: datetime

    company_id: int

    total_amount: Decimal

    company: CompanyResponse

    items: list[PurchaseItemResponse]

    class Config:
        from_attributes = True