from pydantic import BaseModel


class CompanyCreate(BaseModel):
    name: str


class CompanyResponse(BaseModel):

    id: int
    name: str

    model_config = {
        "from_attributes": True
    }