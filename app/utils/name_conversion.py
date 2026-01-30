import json
import os

COUNTRIES_JSON_PATH = os.path.join(os.path.dirname(__file__), '../data/countries.json')

def load_countries():
    with open(COUNTRIES_JSON_PATH, encoding='utf-8') as f:
        data = json.load(f)

    # support either {"countries": [...]} or a plain list [...]
    if isinstance(data, dict) and 'countries' in data and isinstance(data['countries'], list):
        return data['countries']
    if isinstance(data, list):
        return data

    # try to extract list-like values if the JSON is a dict of entries
    if isinstance(data, dict):
        values = list(data.values())
        if values and isinstance(values[0], dict) and 'countryCode' in values[0]:
            return values

    raise ValueError("Unsupported countries.json format")

_countries = load_countries()

# Build lookup dictionaries for fast conversion
_country_to_currency = {entry['countryCode']: entry['currencyCode'] for entry in _countries}

# reverse mapping
_currency_to_country = {entry['currencyCode']: entry['countryCode'] for entry in _countries}

def country_to_currency(country_code: str) -> str:
    """Convert country code to currency code."""
    return _country_to_currency.get(country_code)


def currency_to_country(currency_code: str) -> str:
    """Convert currency code to country code."""
    return _currency_to_country.get(currency_code)
