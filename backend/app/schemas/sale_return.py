

from pydantic import BaseModel, Field


class SaleReturnCreate(BaseModel):
    sale_item_id: int = Field(..., gt=0, description="ID of the sale item")
    quantity: int = Field(..., gt=0, description="Quantity to return")
    reason: str | None = Field(None, description="Reason for return")