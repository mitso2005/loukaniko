import requests
from app.config import WORLD_BANK_API_BASE_URL, WORLD_BANK_API_VERSION


def get_cpi_data(country_code: str, start: int, end: int):
    url = f"{WORLD_BANK_API_BASE_URL}{WORLD_BANK_API_VERSION}/country/{country_code}/indicator/FP.CPI.TOTL"
    params = {
        "date": f"{start}:{end}",
        "format": "json"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()