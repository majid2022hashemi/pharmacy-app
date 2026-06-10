#  pharmacy_app/backend/app/schemas/sale.py
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_serializer

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

    model_config = {"from_attributes": True}


class SaleResponse(BaseModel):
    id: int
    sale_number: str
    customer_name: str | None
    total_amount: Decimal
    created_at: datetime | None = None
    items: list[SaleItemResponse]

    model_config = {"from_attributes": True}

    @field_serializer("created_at")
    def serialize_created_at(self, v: datetime | None) -> str | None:
        return v.isoformat() if v else None
