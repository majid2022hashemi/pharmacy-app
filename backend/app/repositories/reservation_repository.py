from app.models import StockReservation


class ReservationRepository:

    @staticmethod
    def create(
        db,
        medicine_id,
        batch_id,
        quantity,
    ):

        reservation = StockReservation(
            medicine_id=medicine_id,
            batch_id=batch_id,
            quantity=quantity,
            status="active",
        )

        db.add(reservation)
        return reservation

    @staticmethod
    def release(reservation):
        reservation.status = "released"

    @staticmethod
    def commit(reservation):
        reservation.status = "committed"