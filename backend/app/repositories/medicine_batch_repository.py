# backend/app/repositories/medicine_batch_repository.py

from datetime import date
from sqlalchemy.orm import Session
from app.models import MedicineBatch


class MedicineBatchRepository:

    @staticmethod
    def create(
        db: Session,
        medicine_id: int,
        batch_number: str,
        expiry_date: date,
        purchase_price: float,
        sale_price: float,
        quantity: int,
    ) -> MedicineBatch:
        """
        ایجاد یک دسته دارویی جدید
        """
        batch = MedicineBatch(
            medicine_id=medicine_id,
            batch_number=batch_number,
            expiry_date=expiry_date,
            purchase_price=purchase_price,
            sale_price=sale_price,
            quantity_received=quantity,
            quantity_remaining=quantity,
        )
        db.add(batch)
        db.flush()  # مقدار id بعد از flush آماده است
        return batch

    @staticmethod
    def get_available_batches(
        db: Session,
        medicine_id: int,
    ) -> list[MedicineBatch]:
        """دریافت همه دسته‌های موجود دارو با موجودی مثبت"""
        return (
            db.query(MedicineBatch)
            .filter(
                MedicineBatch.medicine_id == medicine_id,
                MedicineBatch.quantity_remaining > 0,
            )
            .order_by(MedicineBatch.expiry_date.asc(), MedicineBatch.id.asc())
            .all()
        )

    @staticmethod
    def get_available_batches_for_update(
        db: Session,
        medicine_id: int,
    ) -> list[MedicineBatch]:
        """
        دریافت دسته‌های موجود دارو با موجودی مثبت و قفل row برای عملیات transaction
        """
        return (
            db.query(MedicineBatch)
            .filter(
                MedicineBatch.medicine_id == medicine_id,
                MedicineBatch.quantity_remaining > 0,
            )
            .order_by(MedicineBatch.expiry_date.asc(), MedicineBatch.id.asc())
            .with_for_update()
            .all()
        )

    @staticmethod
    def get_first_available_batch(
        db: Session,
        medicine_id: int,
    ) -> MedicineBatch | None:
        """دریافت اولین دسته موجود دارو با موجودی مثبت"""
        return (
            db.query(MedicineBatch)
            .filter(
                MedicineBatch.medicine_id == medicine_id,
                MedicineBatch.quantity_remaining > 0,
            )
            .order_by(MedicineBatch.expiry_date.asc(), MedicineBatch.id.asc())
            .first()
        )

    @staticmethod
    def get_by_id(
        db: Session,
        batch_id: int,
    ) -> MedicineBatch | None:
        """دریافت دسته بر اساس شناسه"""
        return db.query(MedicineBatch).filter(MedicineBatch.id == batch_id).first()

    @staticmethod
    def get_by_batch_number(
        db: Session,
        batch_number: str,
    ) -> MedicineBatch | None:
        """دریافت دسته بر اساس شماره دسته"""
        return (
            db.query(MedicineBatch)
            .filter(MedicineBatch.batch_number == batch_number)
            .first()
        )

    @staticmethod
    def get_expired_batches(
        db: Session,
        today: date,
    ) -> list[MedicineBatch]:
        """دریافت دسته‌های منقضی شده"""
        return (
            db.query(MedicineBatch)
            .filter(
                MedicineBatch.expiry_date < today,
                MedicineBatch.quantity_remaining > 0,
            )
            .order_by(MedicineBatch.expiry_date.asc())
            .all()
        )

    @staticmethod
    def get_active_batches_by_medicine(
        db: Session,
        medicine_id: int,
    ) -> list[MedicineBatch]:
        """دریافت دسته‌های فعال یک دارو (با موجودی مثبت)"""
        return (
            db.query(MedicineBatch)
            .filter(
                MedicineBatch.medicine_id == medicine_id,
                MedicineBatch.quantity_remaining > 0,
            )
            .all()
        )