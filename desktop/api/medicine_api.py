import requests
from config import BASE_URL
from api.auth_api import get_auth_headers


def get_medicines():
    r = requests.get(f"{BASE_URL}/medicines", headers=get_auth_headers(), timeout=10)
    r.raise_for_status()
    return r.json()


def search_medicines(q: str = "", otc: bool | None = None) -> list[dict]:
    params = {}
    if q:
        params["q"] = q
    if otc is not None:
        params["otc"] = "true" if otc else "false"
    r = requests.get(f"{BASE_URL}/medicines", params=params, headers=get_auth_headers(), timeout=10)
    r.raise_for_status()
    return r.json()


def get_medicine_by_code(code: str) -> dict | None:
    try:
        r = requests.get(
            f"{BASE_URL}/medicines/by-code/{code}",
            headers=get_auth_headers(),
            timeout=10,
        )
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def create_medicine(code: str, name: str, virtual_code: str | None = None,
                    trade_name: str | None = None, generic_name: str | None = None,
                    dosage_form: str | None = None, strength: str | None = None,
                    is_prescription: bool = False, current_stock: int = 0,
                    sale_price=None, default_quantity: int = 1,
                    category_id=None, company_id=None) -> dict:
    r = requests.post(
        f"{BASE_URL}/medicines",
        json={
            "code": code,
            "virtual_code": virtual_code,
            "name": name,
            "trade_name": trade_name,
            "generic_name": generic_name,
            "dosage_form": dosage_form,
            "strength": strength,
            "is_prescription": is_prescription,
            "current_stock": current_stock,
            "sale_price": sale_price,
            "default_quantity": default_quantity,
            "category_id": category_id,
            "company_id": company_id,
        },
        headers=get_auth_headers(),
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


def update_medicine(medicine_id: int, data: dict) -> dict:
    r = requests.patch(
        f"{BASE_URL}/medicines/{medicine_id}",
        json=data,
        headers=get_auth_headers(),
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


def get_categories() -> list[dict]:
    r = requests.get(f"{BASE_URL}/categories/", headers=get_auth_headers(), timeout=10)
    r.raise_for_status()
    return r.json()


def get_companies() -> list[dict]:
    r = requests.get(f"{BASE_URL}/companies/", headers=get_auth_headers(), timeout=10)
    r.raise_for_status()
    return r.json()


def create_purchase_invoice(data: dict) -> dict:
    r = requests.post(
        f"{BASE_URL}/purchase-invoices",
        json=data,
        headers=get_auth_headers(),
        timeout=15,
    )
    r.raise_for_status()
    return r.json()
