from datetime import datetime

from pydantic import BaseModel

from app.schemas.company import CompanyResponse
from app.schemas.purchase_item import PurchaseItemResponse


class PurchaseInvoiceResponse(BaseModel):

    id: int

    invoice_number: str

    purchase_date: datetime

    company_id: int

    company: CompanyResponse

    items: list[PurchaseItemResponse]

    model_config = {
        "from_attributes": True
    }