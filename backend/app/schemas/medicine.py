from pydantic import BaseModel
from decimal import Decimal


class MedicineCreate(BaseModel):

    code: str

    name: str

    generic_name: str | None = None

    dosage_form: str | None = None

    strength: str | None = None

    sale_price: Decimal | None = None

    current_stock: int = 0

class MedicineResponse(BaseModel):

    id: int

    code: str

    name: str

    generic_name: str | None

    dosage_form: str | None

    strength: str | None

    sale_price: Decimal | None

    current_stock: int

    model_config = {
        "from_attributes": True
    }