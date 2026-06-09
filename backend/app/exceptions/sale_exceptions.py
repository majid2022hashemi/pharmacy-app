# backend/app/exceptions/sale_exceptions.py

class MedicineNotFoundError(Exception):
    pass


class InsufficientStockError(Exception):
    pass