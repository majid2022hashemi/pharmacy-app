from pydantic import BaseModel, Field


class MedicineCreate(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=255,
    )

    quantity: int = Field(
        ge=0,
    )


class MedicineResponse(BaseModel):

    id: int
    name: str
    quantity: int

    model_config = {
        "from_attributes": True
    }