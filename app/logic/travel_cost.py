import json
from pathlib import Path
from typing import Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.services.fx import (
    get_latest_rate,
    get_historical_average_rate,
    get_supported_currencies,
)
from app.services.cpi import get_latest_cpi, get_historical_average_cpi
from app.utils.name_conversion import country_to_currency


def calculate_travel_value_index_corrected(
    base_country_code: str,
    target_country_code: str,
    years: int = 20
) -> Dict[str, float]:
    """
    Corrected approach: Compare REAL (inflation-adjusted) exchange rates.
    """
    base_currency = country_to_currency(base_country_code)
    target_currency = country_to_currency(target_country_code)
    
    if not base_currency or not target_currency:
        raise ValueError("Invalid country codes")

    # Get current values
    fx_current = get_latest_rate(base_currency, target_currency)
    base_cpi_current = get_latest_cpi(base_country_code)
    target_cpi_current = get_latest_cpi(target_country_code)
    
    # Get historical averages
    fx_avg = get_historical_average_rate(base_currency, target_currency, years)
    base_cpi_avg = get_historical_average_cpi(base_country_code, years)
    target_cpi_avg = get_historical_average_cpi(target_country_code, years)
    
    # Calculate REAL exchange rate (inflation-adjusted)
    # This normalizes for CPI base year differences
    real_fx_current = fx_current * (base_cpi_current / target_cpi_current)
    real_fx_historical = fx_avg * (base_cpi_avg / target_cpi_avg)
    
    # Travel value index: current real rate / historical real rate
    # > 1 = target currency weaker than historical norm = good value
    # < 1 = target currency stronger than historical norm = expensive
    value_index = real_fx_current / real_fx_historical
    
    pct_vs_historical = (value_index - 1.0) * 100
    
    return {
        "base_country": base_country_code,
        "target_country": target_country_code,
        "real_exchange_rate_current": real_fx_current,
        "real_exchange_rate_historical": real_fx_historical,
        "travel_value_index": value_index,
        "percent_vs_historical": pct_vs_historical,
        "interpretation": (
            f"{'Better' if pct_vs_historical > 0 else 'Worse'} value by "
            f"{abs(pct_vs_historical):.1f}% compared to {years}-year average"
        )
    }
    
def rank_countries_by_travel_value(
    base_country_code: str,
    years: int = 20,
    max_workers: int = 20,
):
    """Rank countries by travel value from a base country perspective."""
    countries_path = Path(__file__).parent.parent / "data" / "countries.json"

    with open(countries_path, encoding="utf-8") as f:
        data = json.load(f)

    country_list = data.get("countries", data)
    supported_currencies = get_supported_currencies()

    results = []

    def process_country(entry):
        target_code = entry.get("countryCode")

        if not target_code:
            print("Skipping entry with no countryCode")
            return None

        if target_code == base_country_code:
            print(f"Skipping {target_code}: base country")
            return None

        # Check if country's currency is supported
        target_currency = country_to_currency(target_code)
        if not target_currency or target_currency not in supported_currencies:
            print(f"Skipping {target_code}: currency {target_currency} not supported")
            return None

        try:
            res = calculate_travel_value_index_corrected(
                base_country_code,
                target_code,
                years
            )

            value = res.get("travel_value_index")
            if value is None:
                print(f"Skipping {target_code}: travel_value_index is None")
                return None

            # ✅ SUCCESS LOG
            status = "cheap" if value > 1 else "expensive"
            print(
                f"✔ {target_code} recorded: "
                f"travel_value_index={value:.3f} ({status})"
            )

            return {
                "country_code": target_code,
                "travel_value_index": value
            }

        except Exception as e:
            print(f"Skipping {target_code}: {e}")
            return None

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(process_country, entry)
            for entry in country_list
        ]

        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    results.sort(
        key=lambda x: x["travel_value_index"],
        reverse=True,
    )

    return results