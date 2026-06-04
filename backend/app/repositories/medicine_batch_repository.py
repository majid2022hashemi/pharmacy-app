# backend/app/repositories/medicine_batch_repository.py

from sqlalchemy import select

from app.models import MedicineBatch


class MedicineBatchRepository:

    @staticmethod
    def create(
        db,
        medicine_id,
        batch_number,
        expiry_date,
        purchase_price,
        sale_price,
        quantity,
    ):

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

        return batch

    @staticmethod
    def get_available_batches(
        db,
        medicine_id,
    ):

        return (
            db.query(MedicineBatch)
            .filter(
                MedicineBatch.medicine_id == medicine_id,
                MedicineBatch.quantity_remaining > 0,
            )
            .order_by(
                MedicineBatch.expiry_date.asc(),
                MedicineBatch.id.asc(),
            )
            .all()
        )
    
    @staticmethod
    def get_first_available_batch(
        db,
        medicine_id,
    ):

        return (
            db.query(MedicineBatch)
            .filter(
                MedicineBatch.medicine_id == medicine_id,
                MedicineBatch.quantity_remaining > 0,
            )
            .order_by(
                MedicineBatch.expiry_date.asc(),
                MedicineBatch.id.asc(),
            )
            .first()
        )