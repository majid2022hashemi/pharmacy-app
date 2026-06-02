# pharmacy_app/backend/app/schemas/medicine.py
from decimal import Decimal
from pydantic import BaseModel

from app.schemas.category import CategoryResponse


class MedicineCreate(BaseModel):

    code: str
    name: str

    generic_name: str | None = None
    dosage_form: str | None = None
    strength: str | None = None

    sale_price: Decimal | None = None

    current_stock: int = 0

    category_id: int | None = None


class MedicineResponse(BaseModel):

    id: int

    code: str
    name: str

    generic_name: str | None
    dosage_form: str | None
    strength: str | None

    sale_price: Decimal | None
    current_stock: int

    category_id: int | None

    category: CategoryResponse | None

    model_config = {
        "from_attributes": True
    }
    