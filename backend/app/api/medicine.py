from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Medicine
from app.schemas.medicine import (
    MedicineCreate,
    MedicineResponse,
)

router = APIRouter()


@router.post(
    "/medicines",
    response_model=MedicineResponse,
)
def create_medicine(
    medicine: MedicineCreate,
    db: Session = Depends(get_db),
):

    db_medicine = Medicine(
        name=medicine.name,
        quantity=medicine.quantity,
    )

    db.add(db_medicine)

    db.commit()

    db.refresh(db_medicine)

    return db_medicine


@router.get(
    "/medicines",
    response_model=list[MedicineResponse],
)
def get_medicines(
    db: Session = Depends(get_db),
):

    medicines = db.query(Medicine).all()

    return medicines