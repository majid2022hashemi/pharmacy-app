# backend/app/services/sale_service.py

from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import SaleItem

from app.repositories.medicine_repository import (
    MedicineRepository,
)

from app.repositories.sale_repository import (
    SaleRepository,
)

from app.exceptions.sale_exceptions import (
    MedicineNotFoundError,
    InsufficientStockError,
)

from app.schemas.sale import (
    SaleItemCreate,
)


def create_sale_service(
    db: Session,
    sale_number: str,
    customer_name: str | None,
    items: list[SaleItemCreate],
):

    total_amount = Decimal("0")

    sale = SaleRepository.create(
        db=db,
        sale_number=sale_number,
        customer_name=customer_name,
    )

    db.flush()

    for item in items:

        medicine = MedicineRepository.get_by_id(
            db=db,
            medicine_id=item.medicine_id,
        )

        if medicine is None:
            raise MedicineNotFoundError(
                f"Medicine {item.medicine_id} not found"
            )

        if medicine.current_stock < item.quantity:
            raise InsufficientStockError(
                f"Not enough stock for {medicine.name}"
            )

        medicine.current_stock -= item.quantity

        db_item = SaleItem(
            sale_id=sale.id,
            medicine_id=item.medicine_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
        )

        db.add(db_item)

        total_amount += (
            item.quantity *
            item.unit_price
        )

    sale.total_amount = total_amount

    db.commit()

    db.refresh(sale)

    return sale