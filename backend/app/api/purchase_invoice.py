from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import PurchaseInvoice
from app.schemas.purchase_invoice import PurchaseInvoiceResponse
from app.schemas.purchase_invoice_create import PurchaseInvoiceCreate
from app.services.purchase_service import PurchaseService

router = APIRouter()


@router.post("/purchase-invoices", response_model=PurchaseInvoiceResponse)
def create_purchase_invoice(
    invoice: PurchaseInvoiceCreate,
    db: Session = Depends(get_db)
):

    return PurchaseService.create_purchase_invoice(
        db=db,
        invoice_number=invoice.invoice_number,
        company_id=invoice.company_id,
        items=invoice.items,
    )


@router.get("/purchase-invoices", response_model=list[PurchaseInvoiceResponse])
def get_purchase_invoices(db: Session = Depends(get_db)):

    return (
        db.query(PurchaseInvoice)
        .options(
            joinedload(PurchaseInvoice.company),
            joinedload(PurchaseInvoice.items),
        )
        .all()
    )