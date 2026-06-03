#  pharmacy_app/backend/app/schemas/sale.py
from decimal import Decimal
from pydantic import BaseModel, Field

from app.schemas.medicine import MedicineResponse


class SaleItemCreate(BaseModel):

    medicine_id: int

    quantity: int = Field(gt=0)

    unit_price: Decimal = Field(gt=0)


class SaleCreate(BaseModel):

    sale_number: str

    customer_name: str | None = None

    items: list[SaleItemCreate]


class SaleItemResponse(BaseModel):

    id: int

    medicine_id: int

    quantity: int

    unit_price: Decimal

    medicine: MedicineResponse

    model_config = {
        "from_attributes": True
    }


class SaleResponse(BaseModel):

    id: int

    sale_number: str

    customer_name: str | None

    total_amount: Decimal

    items: list[SaleItemResponse]

    model_config = {
        "from_attributes": True
    }