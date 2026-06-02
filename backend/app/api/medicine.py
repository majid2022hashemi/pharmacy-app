# pharmacy_app/backend/app/api/medicine.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import (
    Session,
    joinedload,
)

from app.database import get_db
from app.models import Medicine

from app.schemas.medicine import (
    MedicineCreate,
    MedicineResponse,
)

router = APIRouter()


@router.get(
    "/medicines",
    response_model=list[MedicineResponse],
)
def get_medicines(
    db: Session = Depends(get_db),
):

    medicines = (
        db.query(Medicine)
        .options(
            joinedload(Medicine.category)
        )
        .all()
    )

    return medicines