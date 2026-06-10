# pharmacy_app/backend/app/schemas/medicine.py
from decimal import Decimal
from pydantic import BaseModel
from app.schemas.category import CategoryResponse
from app.schemas.company import CompanyResponse


class MedicineCreate(BaseModel):
    code: str
    name: str
    virtual_code: str | None = None
    trade_name: str | None = None
    generic_name: str | None = None
    dosage_form: str | None = None
    strength: str | None = None
    is_prescription: bool = False
    sale_price: Decimal | None = None
    current_stock: int = 0
    default_quantity: int = 1
    category_id: int | None = None
    company_id: int | None = None


class MedicineUpdate(BaseModel):
    name: str | None = None
    virtual_code: str | None = None
    trade_name: str | None = None
    generic_name: str | None = None
    dosage_form: str | None = None
    strength: str | None = None
    is_prescription: bool | None = None
    sale_price: Decimal | None = None
    default_quantity: int | None = None
    category_id: int | None = None
    company_id: int | None = None


class MedicineResponse(BaseModel):
    id: int
    code: str
    virtual_code: str | None
    name: str
    trade_name: str | None
    generic_name: str | None
    dosage_form: str | None
    strength: str | None
    is_prescription: bool
    sale_price: Decimal | None
    current_stock: int
    default_quantity: int
    category_id: int | None
    company_id: int | None
    category: CategoryResponse | None
    company: CompanyResponse | None

    model_config = {
        "from_attributes": True
    }
