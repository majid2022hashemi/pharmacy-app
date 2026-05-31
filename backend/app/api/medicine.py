# pharmacy_app/backend/app/api/medicine.py
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
        code=medicine.code,
        name=medicine.name,
        generic_name=medicine.generic_name,
        dosage_form=medicine.dosage_form,
        strength=medicine.strength,
        sale_price=medicine.sale_price,
        current_stock=medicine.current_stock,
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