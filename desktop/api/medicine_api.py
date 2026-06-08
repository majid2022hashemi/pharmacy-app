import requests
from config import BASE_URL


def get_medicines():
    response = requests.get(f"{BASE_URL}/medicines")
    response.raise_for_status()
    return response.json()


def create_medicine(code, name, current_stock=0, sale_price=None, category_id=None, company_id=None):
    response = requests.post(
        f"{BASE_URL}/medicines",
        json={
            "code": code,
            "name": name,
            "current_stock": current_stock,
            "sale_price": sale_price,
            "category_id": category_id,
            "company_id": company_id,
        },
    )

    response.raise_for_status()
    return response.json()