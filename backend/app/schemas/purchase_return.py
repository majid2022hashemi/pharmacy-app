# backend/app/schemas/purchase_return.py

from pydantic import BaseModel, Field
from typing import Optional


class PurchaseReturnCreate(BaseModel):

    purchase_item_id: int = Field(
        ...,
        description="ID of purchase item to return",
    )

    quantity: int = Field(
        ...,
        gt=0,
        description="Quantity to return (must be greater than 0)",
    )

    reason: Optional[str] = Field(
        None,
        description="Reason for return (optional)",
    )


class PurchaseReturnResponse(BaseModel):

    id: int
    purchase_item_id: int
    quantity: int
    reason: Optional[str]

    class Config:
        from_attributes = True