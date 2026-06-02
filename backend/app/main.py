from fastapi import FastAPI

from app.database import (
    Base,
    engine,
)

from app.models import (
    Medicine,
    Category,
)

from app.api.medicine import (
    router as medicine_router,
)

from app.api.category import (
    router as category_router,
)

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(medicine_router)
app.include_router(category_router)


@app.get("/")
def root():
    return {"message": "Pharmacy API"}