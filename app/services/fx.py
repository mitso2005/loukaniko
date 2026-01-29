import requests
from app.config import FRANKFURTER_API_BASE_URL, FRANKFURTER_API_VERSION

def get_latest_rates(base: str = "EUR"):
    url = f"{FRANKFURTER_API_BASE_URL}{FRANKFURTER_API_VERSION}/latest"
    params = {"base": base}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()