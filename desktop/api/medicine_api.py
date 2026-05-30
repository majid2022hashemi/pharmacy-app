import requests

BASE_URL = "http://127.0.0.1:8001"


def get_medicines():
    response = requests.get(f"{BASE_URL}/medicines")
    response.raise_for_status()
    return response.json()