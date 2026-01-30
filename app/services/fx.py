import requests
from app.config import FRANKFURTER_API_BASE_URL, FRANKFURTER_API_VERSION

def get_latest_rates(base: str = "EUR", symbols: list[str] = None):
    url = f"{FRANKFURTER_API_BASE_URL}{FRANKFURTER_API_VERSION}/latest"
    params = {"base": base}
    if symbols:
        params["symbols"] = ",".join(symbols)
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def get_latest_rate(base: str = "EUR", symbol: str = None):
    url = f"{FRANKFURTER_API_BASE_URL}{FRANKFURTER_API_VERSION}/latest"
    params = {"base": base}
    if symbol:
        params["symbols"] = symbol
    response = requests.get(url, params=params)
    response.raise_for_status()
    return list(response.json()["rates"].values())[0]

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

def get_year_average_rate(base: str, target: str, year: int) -> float:
    """
    Returns the average exchange rate from base to target for all days in the given year.
    """
    date_start = f"{year}-01-01"
    date_end = f"{year}-12-31"
    url = f"{FRANKFURTER_API_BASE_URL}{FRANKFURTER_API_VERSION}/{date_start}..{date_end}"
    params = {"base": base, "symbols": target}
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    rates = [day[target] for day in data.get("rates", {}).values() if target in day]
    if not rates:
        raise ValueError(f"No rates found for {base} to {target} in {year}")
    return sum(rates) / len(rates)

def get_historical_average_rate(base: str, target: str, years: int) -> dict:
    """
    Returns a dict of {year: average_rate} for the last `years` years ending at current year minus 1.
    """
    from datetime import datetime
    end_year = datetime.now().year - 1
    total = 0.0 # Sum of rates
    na = 0  # Count of years with no data
    for year in range(end_year, end_year - years, -1):
        try:
            total += get_year_average_rate(base, target, year)
        except Exception:
            na += 1  # Adjust years if data is missing
            
    avg = total / (years - na)
    
    return avg