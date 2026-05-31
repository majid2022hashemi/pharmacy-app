# pharmacy_app/backend/app/main.py
from fastapi import FastAPI

from app.database import engine
from app.models import Base
from app.api.medicine import router as medicine_router


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(medicine_router)


@app.get("/")
def root():
    return {"message": "Pharmacy API"}