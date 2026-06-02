# backend/app/api/category.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category
from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
)

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)

@router.get(
    "/",
    response_model=list[CategoryResponse],
)
def get_categories(
    db: Session = Depends(get_db),
):
    return db.query(Category).all()


@router.post(
    "/",
    response_model=CategoryResponse,
)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
):
    db_category = Category(
        name=category.name,
    )

    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    return db_category


