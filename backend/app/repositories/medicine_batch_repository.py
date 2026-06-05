# backend/app/repositories/medicine_batch_repository.py

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

        db.flush()

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
    def get_available_batches_for_update(
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
            .with_for_update()
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

    @staticmethod
    def get_by_id(
        db,
        batch_id,
    ):

        return (
            db.query(MedicineBatch)
            .filter(
                MedicineBatch.id == batch_id
            )
            .first()
        )

    @staticmethod
    def get_by_batch_number(
        db,
        batch_number,
    ):

        return (
            db.query(MedicineBatch)
            .filter(
                MedicineBatch.batch_number == batch_number
            )
            .first()
        )

    @staticmethod
    def get_expired_batches(
        db,
        today,
    ):

        return (
            db.query(MedicineBatch)
            .filter(
                MedicineBatch.expiry_date < today,
                MedicineBatch.quantity_remaining > 0,
            )
            .order_by(
                MedicineBatch.expiry_date.asc()
            )
            .all()
        )