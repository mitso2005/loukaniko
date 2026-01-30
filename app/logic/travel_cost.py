from app.services.fx import get_latest_rates, get_supported_currencies, get_latest_rate, get_historical_rates
from app.services.cpi import get_cpi_data, get_latest_cpi, get_cpi_historical

def real_travel_value(destination_code: str, base_currency: str):
    destination_currency = destination_code  # Simplified assumption; in practice, map country code to currency code
    
    travel_cpi = get_latest_cpi(destination_code)
    base_fx = get_latest_rate(base_currency, destination_currency)
    
    travel_value = {
        "country_code": destination_code,
        "base_currency": base_currency,
        "latest_cpi": travel_cpi,
        "latest_fx": base_fx,
    }
    
    return travel_value