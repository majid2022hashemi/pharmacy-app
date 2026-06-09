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
    MedicineBatch,
    StockMovement,
    StockReservation,
)

from app.api.medicine import router as medicine_router
from app.api.category import router as category_router
from app.api.company import router as company_router
from app.api.purchase_invoice import router as purchase_invoice_router
from app.api.purchase_item import router as purchase_item_router
from app.api.sale import router as sale_router
from app.api.stock_movement import (router as stock_movement_router)
from app.api.sale_return import (router as sale_return_router,)
from app.api.purchase_return import router as purchase_return_router
from app.api.auth import router as auth_router
from app.api.users import router as users_router

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.enums.user_role import UserRole
from app.database import SessionLocal

Base.metadata.create_all(bind=engine)


def create_default_admin():
    db = SessionLocal()
    try:
        if UserRepository.count(db) == 0:
            UserRepository.create(
                db=db,
                username="admin",
                password="admin123",
                full_name="مدیر سیستم",
                role=UserRole.ADMIN,
            )
    finally:
        db.close()


create_default_admin()

app = FastAPI(
    title="Pharmacy API",
    version="1.0.0",
)

app.include_router(medicine_router)
app.include_router(category_router)
app.include_router(company_router)
app.include_router(purchase_invoice_router)
app.include_router(purchase_item_router)
app.include_router(sale_router)
app.include_router(stock_movement_router)
app.include_router(sale_return_router)
app.include_router(purchase_return_router)
app.include_router(auth_router)
app.include_router(users_router)

@app.get("/")
def root():
    return {
        "message": "Pharmacy API"
    }