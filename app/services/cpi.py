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

def get_cpi_historical(country_code: str, year_start: int, year_end: int):
    list_cpi = []
    url = f"{WORLD_BANK_API_BASE_URL}{WORLD_BANK_API_VERSION}/country/{country_code}/indicator/FP.CPI.TOTL"
    params = {
        "date": f"{year_start}:{year_end}",
        "format": "json"
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    if len(data) > 1 and isinstance(data[1], list):
        for entry in data[1]:
            year = entry.get("date")
            cpi_value = entry.get("value")
            list_cpi.append({"year": year, "cpi": cpi_value})
        
    return list_cpi