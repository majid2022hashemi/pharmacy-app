from fastapi import FastAPI

from app.database import (
    Base,
    engine,
)

from app.models import (
    Medicine,
    Category,
    PurchaseInvoice,
    PurchaseItem,
)

from app.api.medicine import (
    router as medicine_router,
)

from app.api.category import (
    router as category_router,
)

from app.api.company import router as company_router
from app.api.purchase_invoice import router as purchase_invoice_router


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(medicine_router)
app.include_router(category_router)
app.include_router(company_router)
app.include_router(
    purchase_invoice_router
)

@app.get("/")
def root():
    return {"message": "Pharmacy API"}