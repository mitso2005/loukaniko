import json
import os

from typing import Dict, Optional
from datetime import datetime
from app.services.fx import get_latest_rate, get_year_average_rate, get_historical_average_rate
from app.services.cpi import get_latest_cpi, get_cpi_for_year, get_historical_average_cpi
from app.utils.name_conversion import country_to_currency
from concurrent.futures import ThreadPoolExecutor, as_completed


def calculate_purchasing_power(
    base_country_code: str,
    target_country_code: str
) -> Optional[float]:
    """
    Calculate current purchasing power: how many units of target country's
    goods/services you can buy with 1 unit of base currency.
    
    Formula: FX_rate / Target_CPI
    
    Higher value = more purchasing power in target country
    """
    base_currency = country_to_currency(base_country_code)
    target_currency = country_to_currency(target_country_code)
    
    if not base_currency or not target_currency:
        raise ValueError(f"Cannot map country codes to currencies: {base_country_code}, {target_country_code}")

    # Get current exchange rate (base to target)
    fx_rate = get_latest_rate(base_currency, target_currency)
    if fx_rate is None:
        raise ValueError(f"FX rate not available for {base_currency}/{target_currency}")

    # Get current CPI of target country
    target_cpi = get_latest_cpi(target_country_code)
    if target_cpi is None:
        raise ValueError(f"CPI data not available for {target_country_code}")

    # Purchasing power = how much you can buy per unit of your currency
    return fx_rate / target_cpi


def calculate_historical_purchasing_power(
    base_country_code: str,
    target_country_code: str,
    years: int = 20
) -> Optional[float]:
    """
    Calculate historical average purchasing power over the specified period.
    """
    base_currency = country_to_currency(base_country_code)
    target_currency = country_to_currency(target_country_code)
    
    if not base_currency or not target_currency:
        raise ValueError(f"Cannot map country codes to currencies: {base_country_code}, {target_country_code}")

    end_year = datetime.now().year - 1
    
    total_purchasing_power = 0.0
    valid_years = 0
    
    for year in range(end_year - years + 1, end_year + 1):
        try:
            # Get average FX rate for this year
            fx_avg = get_year_average_rate(base_currency, target_currency, year)
            
            # Get CPI for this year (you may need to add a get_cpi_for_year function)
            target_cpi = get_cpi_for_year(target_country_code, year)
            
            if fx_avg and target_cpi:
                total_purchasing_power += fx_avg / target_cpi
                valid_years += 1
        except Exception:
            continue  # Skip years with missing data
    
    if valid_years == 0:
        raise ValueError(f"No valid data found for {years}-year period")
    
    return total_purchasing_power / valid_years

def calculate_travel_value_index(
    base_country_code: str,
    target_country_code: str,
    years: int = 20
) -> Dict[str, float]:
    """
    Calculate travel value index comparing current purchasing power to historical average.
    
    Index > 1.0: Better value than historical average (good time to visit)
    Index = 1.0: Same value as historical average
    Index < 1.0: Worse value than historical average (expensive compared to usual)
    
    Args:
        base_country_code: Your home country (e.g., 'AU' for Australia)
        target_country_code: Destination country (e.g., 'JP' for Japan)
        years: Number of historical years to compare against (default: 20)
    
    Returns:
        Dictionary with current PP, historical PP, and value score
    """
    current_pp = calculate_purchasing_power(base_country_code, target_country_code)
    historical_pp = calculate_historical_purchasing_power(base_country_code, target_country_code, years)
    
    # Value score: current / historical
    # > 1 = better deal than usual
    # < 1 = worse deal than usual
    value_index = current_pp / historical_pp
    
    # Calculate percentage difference for easier interpretation
    pct_vs_historical = ((value_index - 1.0) * 100)
    
    return {
        "base_country": base_country_code,
        "target_country": target_country_code,
        "current_purchasing_power": current_pp,
        "historical_purchasing_power": historical_pp,
        "travel_value_index": value_index,
        "percent_vs_historical": pct_vs_historical,
        "interpretation": (
            f"{'Better' if pct_vs_historical > 0 else 'Worse'} value by "
            f"{abs(pct_vs_historical):.1f}% compared to {years}-year average"
        )
    }
    
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
    max_workers: int = 20
):
    countries_path = os.path.join(
        os.path.dirname(__file__),
        "../data/countries.json"
    )

    with open(countries_path, encoding="utf-8") as f:
        data = json.load(f)

    country_list = data.get("countries", data)

    results = []

    def process_country(entry):
        target_code = entry.get("countryCode")

        if not target_code:
            print("Skipping entry with no countryCode")
            return None

        if target_code == base_country_code:
            print(f"Skipping {target_code}: base country")
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
        reverse=True
    )

    return results

    
    
    def debug_travel_value(base_country: str, target_country: str):
        base_currency = country_to_currency(base_country)
        target_currency = country_to_currency(target_country)
        
        fx_current = get_latest_rate(base_currency, target_currency)
        fx_avg = get_historical_average_rate(base_currency, target_currency, 20)
        
        cpi_current = get_latest_cpi(target_country)
        cpi_avg = get_historical_average_cpi(target_country, 20)
        
        print(f"\n{base_country} -> {target_country}")
        print(f"Currency pair: {base_currency}/{target_currency}")
        print(f"FX Current: {fx_current}")
        print(f"FX 20yr Avg: {fx_avg}")
        print(f"CPI Current: {cpi_current}")
        print(f"CPI 20yr Avg: {cpi_avg}")
        print(f"Current PP: {fx_current / cpi_current}")
        print(f"Historical PP: {fx_avg / cpi_avg}")