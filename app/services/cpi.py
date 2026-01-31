from typing import Optional
import requests
from app.config import WORLD_BANK_API_BASE_URL, WORLD_BANK_API_VERSION

def get_latest_cpi(country_code: str):
    url = f"{WORLD_BANK_API_BASE_URL}{WORLD_BANK_API_VERSION}/country/{country_code}/indicator/FP.CPI.TOTL"
    params = {
        "format": "json"
    }
    
    data = requests.get(url, params=params).json()

    latest_entry = data[1][0]

    latest_cpi = latest_entry["value"]
    # latest_year = latest_entry["date"]
    
    return latest_cpi

def get_cpi_data(country_code: str, year_start: int, year_end: int):
    url = f"{WORLD_BANK_API_BASE_URL}{WORLD_BANK_API_VERSION}/country/{country_code}/indicator/FP.CPI.TOTL"
    params = {
        "date": f"{year_start}:{year_end}",
        "format": "json"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def get_historical_average_cpi(country_code: str, years: int) -> float:
    from datetime import datetime
    end_year = datetime.now().year - 1
    start_year = end_year - years + 1
    data = get_cpi_data(country_code, start_year, end_year)
    # World Bank API returns a list, with the latest data first
    values = []
    if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list):
        for entry in data[1]:
            value = entry.get('value')
            if value is not None:
                values.append(value)
    if not values:
        raise ValueError("No CPI data available for the requested period.")
    return sum(values) / len(values)

def get_cpi_for_year(country_code: str, year: int) -> Optional[float]:
    """Get CPI value for a specific year."""
    from app.config import WORLD_BANK_API_BASE_URL, WORLD_BANK_API_VERSION
    import requests
    
    url = f"{WORLD_BANK_API_BASE_URL}{WORLD_BANK_API_VERSION}/country/{country_code}/indicator/FP.CPI.TOTL"
    params = {
        "date": str(year),
        "format": "json"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list) and len(data[1]) > 0:
            return data[1][0].get('value')
    except Exception:
        return None
    
    return None