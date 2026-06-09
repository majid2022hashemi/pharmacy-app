import requests
from config import BASE_URL
from api.auth_api import get_auth_headers


def create_sale(data: dict) -> dict:
    r = requests.post(f"{BASE_URL}/sales", json=data, headers=get_auth_headers(), timeout=15)
    r.raise_for_status()
    return r.json()


def get_sales() -> list[dict]:
    r = requests.get(f"{BASE_URL}/sales", headers=get_auth_headers(), timeout=10)
    r.raise_for_status()
    return r.json()


def get_sale(sale_id: int) -> dict:
    r = requests.get(f"{BASE_URL}/sales/{sale_id}", headers=get_auth_headers(), timeout=10)
    r.raise_for_status()
    return r.json()


def return_sale_item(sale_id: int, sale_item_id: int, quantity: int, reason: str = "") -> dict:
    r = requests.post(
        f"{BASE_URL}/sales/{sale_id}/return",
        json={"sale_item_id": sale_item_id, "quantity": quantity, "reason": reason},
        headers=get_auth_headers(),
        timeout=10,
    )
    r.raise_for_status()
    return r.json()
