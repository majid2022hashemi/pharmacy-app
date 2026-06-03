# backend/app/repositories/sale_repository.py

from app.models import Sale


class SaleRepository:

    @staticmethod
    def create(
        db,
        sale_number,
        customer_name,
    ):

        sale = Sale(
            sale_number=sale_number,
            customer_name=customer_name,
            total_amount=0,
        )

        db.add(sale)

        return sale