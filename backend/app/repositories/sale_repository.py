# pharmacy_app/backend/app/repositories/sale_repository.py

from decimal import Decimal

from sqlalchemy.orm import joinedload

from app.models import (
    Sale,
    SaleItem,
    Medicine,
)


class SaleRepository:

    @staticmethod
    def create_sale(
        db,
        sale_number,
        customer_name,
    ):

        sale = Sale(
            sale_number=sale_number,
            customer_name=customer_name,
            total_amount=Decimal("0"),
        )

        db.add(sale)

        db.flush()

        return sale

    @staticmethod
    def create_item(
        db,
        sale_id,
        medicine_id,
        batch_id,
        quantity,
        unit_price,
    ):

        item = SaleItem(
            sale_id=sale_id,
            medicine_id=medicine_id,
            batch_id=batch_id,
            quantity=quantity,
            unit_price=unit_price,
        )

        db.add(item)

        return item

    @staticmethod
    def get_by_id(
        db,
        sale_id,
    ):

        return (
            db.query(Sale)
            .options(
                joinedload(Sale.items)
                .joinedload(SaleItem.medicine)
                .joinedload(Medicine.category),

                joinedload(Sale.items)
                .joinedload(SaleItem.medicine)
                .joinedload(Medicine.company),

                joinedload(Sale.items)
                .joinedload(SaleItem.batch),
            )
            .filter(
                Sale.id == sale_id
            )
            .first()
        )

    @staticmethod
    def get_all(
        db,
    ):

        return (
            db.query(Sale)
            .options(
                joinedload(Sale.items)
                .joinedload(SaleItem.medicine)
                .joinedload(Medicine.category),

                joinedload(Sale.items)
                .joinedload(SaleItem.medicine)
                .joinedload(Medicine.company),

                joinedload(Sale.items)
                .joinedload(SaleItem.batch),
            )
            .order_by(
                Sale.id.desc()
            )
            .all()
        )