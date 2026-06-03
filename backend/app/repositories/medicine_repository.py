from sqlalchemy.orm import Session

from app.models import Medicine


class MedicineRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        medicine_id: int,
    ):

        return (
            db.query(Medicine)
            .filter(
                Medicine.id == medicine_id
            )
            .first()
        )

    @staticmethod
    def update_stock(
        medicine: Medicine,
        quantity: int,
    ):

        medicine.current_stock += quantity