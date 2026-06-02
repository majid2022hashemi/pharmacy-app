# backend/app/api/category.py

from fastapi import APIRouter

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.get("/")
def get_categories():
    return [
        {"id": 1, "name": "Antibiotics"},
        {"id": 2, "name": "Pain Relief"},
    ]