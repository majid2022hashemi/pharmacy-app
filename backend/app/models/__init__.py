# backend/app/models/__init__.py

from app.models.medicine import Medicine
from app.models.category import Category

__all__ = [
    "Medicine",
    "Category",
]