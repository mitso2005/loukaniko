import requests
from app.config import FRANKFURTER_API_BASE_URL, FRANKFURTER_API_VERSION

def get_latest_rates(base: str = "EUR"):
    url = f"{FRANKFURTER_API_BASE_URL}{FRANKFURTER_API_VERSION}/latest"
    params = {"base": base}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def get_supported_currencies():
    url = f"{FRANKFURTER_API_BASE_URL}{FRANKFURTER_API_VERSION}/currencies"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_historical_rates(date_start: str = "2000-01-01", date_end: str = "2026-01-01", base: str = "EUR"):
    url = f"{FRANKFURTER_API_BASE_URL}{FRANKFURTER_API_VERSION}/{date_start}..{date_end}"
    params = {"base": base}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()