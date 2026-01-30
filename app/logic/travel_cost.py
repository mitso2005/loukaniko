
from app.services.fx import get_latest_rate
from app.services.cpi import get_latest_cpi
from app.utils.name_conversion import country_to_currency


def real_value(base_country_code: str, target_country_code: str):
    base_currency = country_to_currency(base_country_code)
    target_currency = country_to_currency(target_country_code)
    if not base_currency or not target_currency:
        raise ValueError("Invalid country")

    # Get latest CPI values
    base_cpi = get_latest_cpi(base_country_code)
    target_cpi = get_latest_cpi(target_country_code)
    if base_cpi is None or target_cpi is None:
        raise ValueError("CPI data not available for one or both countries")

    # Get latest FX rate from base to target
    fx = get_latest_rate(base_currency, target_currency)
    if fx is None:
        raise ValueError("FX rate not available for currency pair")

    real_val = fx * (base_cpi / target_cpi)
    
    return real_val

