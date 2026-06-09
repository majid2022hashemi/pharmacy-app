import requests
from config import BASE_URL
from api.auth_api import get_auth_headers


def get_users() -> list[dict]:
    r = requests.get(f"{BASE_URL}/users/", headers=get_auth_headers(), timeout=10)
    r.raise_for_status()
    return r.json()


def create_user(data: dict) -> dict:
    r = requests.post(f"{BASE_URL}/users/", json=data, headers=get_auth_headers(), timeout=10)
    r.raise_for_status()
    return r.json()


def update_user(user_id: int, data: dict) -> dict:
    r = requests.patch(f"{BASE_URL}/users/{user_id}", json=data, headers=get_auth_headers(), timeout=10)
    r.raise_for_status()
    return r.json()


def deactivate_user(user_id: int) -> dict:
    r = requests.patch(f"{BASE_URL}/users/{user_id}/deactivate", headers=get_auth_headers(), timeout=10)
    r.raise_for_status()
    return r.json()


def activate_user(user_id: int) -> dict:
    r = requests.patch(f"{BASE_URL}/users/{user_id}/activate", headers=get_auth_headers(), timeout=10)
    r.raise_for_status()
    return r.json()


def admin_reset_password(user_id: int, new_password: str) -> None:
    r = requests.patch(
        f"{BASE_URL}/users/{user_id}/reset-password",
        json={"new_password": new_password},
        headers=get_auth_headers(),
        timeout=10,
    )
    r.raise_for_status()
