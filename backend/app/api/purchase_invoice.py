# pharmacy_app/backend/app/api/purchase_invoice.py

from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import (
    Session,
    joinedload,
)

from app.database import get_db

from app.models import (
    PurchaseInvoice,
    PurchaseItem,
)

from app.schemas.purchase_invoice import (
    PurchaseInvoiceResponse,
)

from app.schemas.purchase_invoice_create import (
    PurchaseInvoiceCreate,
)

router = APIRouter()


@router.post(
    "/purchase-invoices",
    response_model=PurchaseInvoiceResponse,
)
def create_purchase_invoice(
    invoice: PurchaseInvoiceCreate,
    db: Session = Depends(get_db),
):

    db_invoice = PurchaseInvoice(
        invoice_number=invoice.invoice_number,
        company_id=invoice.company_id,
    )

    db.add(db_invoice)

    db.flush()

    for item in invoice.items:

        db_item = PurchaseItem(
            purchase_invoice_id=db_invoice.id,
            medicine_id=item.medicine_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
        )

        db.add(db_item)

    db.commit()

    db.refresh(db_invoice)

    return db_invoice


@router.get(
    "/purchase-invoices",
    response_model=list[PurchaseInvoiceResponse],
)
def get_purchase_invoices(
    db: Session = Depends(get_db),
):

    invoices = (
        db.query(PurchaseInvoice)
        .options(
            joinedload(PurchaseInvoice.company),
            joinedload(PurchaseInvoice.items),
        )
        .all()
    )

    return invoices