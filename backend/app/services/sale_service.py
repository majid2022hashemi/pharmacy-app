from decimal import Decimal

from sqlalchemy.orm import Session

from app.repositories.sale_repository import SaleRepository
from app.repositories.medicine_repository import MedicineRepository
from app.repositories.medicine_batch_repository import MedicineBatchRepository
from app.repositories.reservation_repository import ReservationRepository

from app.exceptions.sale_exceptions import (
    MedicineNotFoundError,
    InsufficientStockError,
)

from app.schemas.sale import SaleItemCreate


class SaleService:

    @staticmethod
    def create_sale(
        db: Session,
        sale_number: str,
        customer_name: str | None,
        items: list[SaleItemCreate],
    ):

        try:

            sale = SaleRepository.create_sale(
                db=db,
                sale_number=sale_number,
                customer_name=customer_name,
            )

            total_amount = Decimal("0")

            reservations = []

            for item in items:

                medicine = MedicineRepository.get_by_id(db, item.medicine_id)

                if not medicine:
                    raise MedicineNotFoundError(
                        f"Medicine {item.medicine_id} not found"
                    )

                remaining = item.quantity

                batches = MedicineBatchRepository.get_available_batches_for_update(
                    db,
                    item.medicine_id,
                )

                total_available = sum(b.quantity_remaining for b in batches)

                if total_available < item.quantity:
                    raise InsufficientStockError(
                        f"Not enough stock for {medicine.name}"
                    )

                for batch in batches:

                    if remaining <= 0:
                        break

                    qty = min(remaining, batch.quantity_remaining)

                    # 🔥 reserve stock (not direct deduction)
                    batch.quantity_remaining -= qty

                    reservation = ReservationRepository.create(
                        db=db,
                        medicine_id=item.medicine_id,
                        batch_id=batch.id,
                        quantity=qty,
                    )

                    reservations.append(reservation)

                    SaleRepository.create_item(
                        db=db,
                        sale_id=sale.id,
                        medicine_id=item.medicine_id,
                        batch_id=batch.id,
                        quantity=qty,
                        unit_price=item.unit_price,
                    )

                    remaining -= qty

                medicine.current_stock -= item.quantity

                total_amount += item.quantity * item.unit_price

            sale.total_amount = total_amount

            # commit reservations
            for r in reservations:
                ReservationRepository.commit(r)

            db.commit()
            db.refresh(sale)

            return SaleRepository.get_by_id(db, sale.id)

        except Exception:

            # rollback-safe release
            db.rollback()

            raise