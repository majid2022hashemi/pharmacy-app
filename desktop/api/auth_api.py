import requests
from config import BASE_URL


def login(username: str, password: str) -> dict:
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": password},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def check_username(username: str) -> bool:
    response = requests.get(f"{BASE_URL}/auth/check-username/{username}", timeout=10)
    if response.status_code == 404:
        return False
    response.raise_for_status()
    return True


def reset_password(username: str, national_id: str, birth_date: str, new_password: str) -> None:
    response = requests.post(
        f"{BASE_URL}/auth/reset-password",
        json={
            "username": username,
            "national_id": national_id,
            "birth_date": birth_date,
            "new_password": new_password,
        },
        timeout=10,
    )
    response.raise_for_status()


def get_auth_headers() -> dict:
    from session import Session
    token = Session.token()
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}
