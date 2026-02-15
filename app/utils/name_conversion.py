import json
from pathlib import Path
from typing import Optional

COUNTRIES_JSON_PATH = Path(__file__).parent.parent / "data" / "countries.json"


def load_countries() -> list:
    """Load countries data from JSON file."""
    with open(COUNTRIES_JSON_PATH, encoding="utf-8") as f:
        data = json.load(f)

    # Support either {"countries": [...]} or a plain list [...]
    if isinstance(data, dict) and "countries" in data and isinstance(data["countries"], list):
        return data["countries"]
    if isinstance(data, list):
        return data

    # Try to extract list-like values if the JSON is a dict of entries
    if isinstance(data, dict):
        values = list(data.values())
        if values and isinstance(values[0], dict) and "countryCode" in values[0]:
            return values

    raise ValueError("Unsupported countries.json format")


_countries = load_countries()

# Build lookup dictionaries for fast conversion
_country_to_currency = {entry["countryCode"]: entry["currencyCode"] for entry in _countries}

# Reverse mapping
_currency_to_country = {entry["currencyCode"]: entry["countryCode"] for entry in _countries}


def country_to_currency(country_code: str) -> Optional[str]:
    """Convert country code to currency code."""
    return _country_to_currency.get(country_code)


def currency_to_country(currency_code: str) -> Optional[str]:
    """Convert currency code to country code."""
    return _currency_to_country.get(currency_code)
