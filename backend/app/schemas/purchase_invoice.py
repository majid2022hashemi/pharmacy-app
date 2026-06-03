from datetime import datetime

from pydantic import BaseModel

from app.schemas.company import CompanyResponse


class PurchaseInvoiceCreate(BaseModel):

    invoice_number: str

    company_id: int


class PurchaseInvoiceResponse(BaseModel):

    id: int

    invoice_number: str

    purchase_date: datetime

    company_id: int

    company: CompanyResponse

    model_config = {
        "from_attributes": True
    }