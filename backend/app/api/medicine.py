from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Medicine
from app.schemas.medicine import MedicineCreate, MedicineUpdate, MedicineResponse

router = APIRouter()


@router.post("/medicines", response_model=MedicineResponse)
def create_medicine(medicine: MedicineCreate, db: Session = Depends(get_db)):
    if db.query(Medicine).filter(Medicine.code == medicine.code).first():
        raise HTTPException(status_code=400, detail="کد دارو تکراری است")
    db_medicine = Medicine(
        code=medicine.code,
        virtual_code=medicine.virtual_code,
        name=medicine.name,
        trade_name=medicine.trade_name,
        generic_name=medicine.generic_name,
        dosage_form=medicine.dosage_form,
        strength=medicine.strength,
        is_prescription=medicine.is_prescription,
        sale_price=medicine.sale_price,
        current_stock=medicine.current_stock,
        default_quantity=medicine.default_quantity,
        category_id=medicine.category_id,
        company_id=medicine.company_id,
    )
    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
    return db_medicine


@router.get("/medicines", response_model=list[MedicineResponse])
def get_medicines(
    db: Session = Depends(get_db),
    q: str | None = Query(None),
    otc: bool | None = Query(None),
    category_name: str | None = Query(None),
):
    from app.models.category import Category
    query = db.query(Medicine).options(
        joinedload(Medicine.category),
        joinedload(Medicine.company),
    )
    if q:
        pattern = f"%{q}%"
        query = query.filter(
            Medicine.code.ilike(pattern) |
            Medicine.name.ilike(pattern) |
            Medicine.generic_name.ilike(pattern) |
            Medicine.trade_name.ilike(pattern)
        )
    if otc is not None:
        query = query.filter(Medicine.is_prescription == (not otc))
    if category_name:
        query = query.join(Category).filter(Category.name.ilike(f"%{category_name}%"))
    return query.order_by(Medicine.name).all()


@router.get("/medicines/by-code/{code}", response_model=MedicineResponse)
def get_medicine_by_code(code: str, db: Session = Depends(get_db)):
    med = db.query(Medicine).options(
        joinedload(Medicine.category),
        joinedload(Medicine.company),
    ).filter(Medicine.code == code).first()
    if not med:
        raise HTTPException(status_code=404, detail="دارو یافت نشد")
    return med


@router.patch("/medicines/{medicine_id}", response_model=MedicineResponse)
def update_medicine(medicine_id: int, data: MedicineUpdate, db: Session = Depends(get_db)):
    med = db.query(Medicine).options(
        joinedload(Medicine.category),
        joinedload(Medicine.company),
    ).filter(Medicine.id == medicine_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="دارو یافت نشد")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(med, k, v)
    db.commit()
    db.refresh(med)
    return med
