# backend/app/main.py
from fastapi import FastAPI

from app.database import Base, engine
from app.models import (
    Medicine,
    Category,
    Company,
    PurchaseInvoice,
    PurchaseItem,
    Sale,
    SaleItem,
)
from app.api.medicine import router as medicine_router
from app.api.category import router as category_router
from app.api.company import router as company_router
from app.api.purchase_invoice import router as purchase_invoice_router
from app.api.purchase_item import router as purchase_item_router
from app.api.sale import router as sale_router

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Pharmacy API",
    version="1.0.0",
)

# Include routers
app.include_router(medicine_router)
app.include_router(category_router)
app.include_router(company_router)
app.include_router(purchase_invoice_router)
app.include_router(purchase_item_router)
app.include_router(sale_router)


@app.get("/")
def root():
    return {"message": "Pharmacy API"}