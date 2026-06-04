# backend/app/repositories/medicine_batch_repository.py

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy import asc

from app.models import MedicineBatch


class MedicineBatchRepository:

    # ----------------------------
    # Create Batch
    # ----------------------------
    @staticmethod
    def create(
        db: Session,
        medicine_id: int,
        batch_number: str,
        expiry_date,
        purchase_price,
        sale_price,
        quantity: int,
    ) -> MedicineBatch:

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

    # ----------------------------
    # FIFO SAFE: lock rows
    # ----------------------------
    @staticmethod
    def get_available_batches_for_update(
        db: Session,
        medicine_id: int,
    ):
        """
        FIFO + row-level lock (FOR UPDATE SKIP LOCKED)
        prevents race conditions in concurrent sales.
        """

        return (
            db.execute(
                select(MedicineBatch)
                .where(
                    MedicineBatch.medicine_id == medicine_id,
                    MedicineBatch.quantity_remaining > 0,
                )
                .order_by(
                    asc(MedicineBatch.expiry_date),
                    asc(MedicineBatch.id),
                )
                .with_for_update(skip_locked=True)
            )
            .scalars()
            .all()
        )

    # ----------------------------
    # Normal FIFO read (no lock)
    # ----------------------------
    @staticmethod
    def get_available_batches(
        db: Session,
        medicine_id: int,
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

    # ----------------------------
    # First batch (FIFO)
    # ----------------------------
    @staticmethod
    def get_first_available_batch(
        db: Session,
        medicine_id: int,
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

    # ----------------------------
    # Reserve stock (IMPORTANT)
    # ----------------------------
    @staticmethod
    def reserve_stock(
        batch: MedicineBatch,
        quantity: int,
    ):
        """
        Reserve stock inside a batch (decrease available)
        """
        if batch.quantity_remaining < quantity:
            raise ValueError("Not enough batch stock")

        batch.quantity_remaining -= quantity

    # ----------------------------
    # Release stock (rollback-safe helper)
    # ----------------------------
    @staticmethod
    def release_stock(
        batch: MedicineBatch,
        quantity: int,
    ):
        """
        Return stock back (used in rollback scenarios)
        """
        batch.quantity_remaining += quantity