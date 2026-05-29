from pydantic import BaseModel


class MedicineCreate(BaseModel):
    name: str
    quantity: int


class MedicineResponse(BaseModel):
    id: int
    name: str
    quantity: int

    model_config = {
        "from_attributes": True
    }