from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


DATABASE_URL = (
    "postgresql+psycopg://pharmacy:pharmacy@db:5432/pharmacy_db"
)


engine = create_engine(
    DATABASE_URL,
    echo=True,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()