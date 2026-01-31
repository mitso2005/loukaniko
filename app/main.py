from fastapi import FastAPI
import json
from app.services.fx import get_latest_rates, get_latest_rate, get_supported_currencies, get_historical_rates, get_year_average_rate, get_historical_average_rate
from app.services.cpi import get_cpi_data, get_latest_cpi, get_historical_average_cpi
from app.logic.travel_cost import calculate_travel_value_index, calculate_travel_value_index_corrected
from app.utils.name_conversion import country_to_currency

app = FastAPI()


@app.get("/")
async def root():
    return {"name": "Loukaniko",
            "description": "Travel value data API",
            "version": "v1", 
            }


if __name__ == "__main__":
    # print(json.dumps(get_latest_rates(), indent=2))
    # print(json.dumps(get_latest_rate("AUD", "JPY"), indent=2))
    # print(json.dumps(get_supported_currencies(), indent=2))
    # print(json.dumps(get_historical_rates(), indent=2))
    # print(json.dumps(get_cpi_data("US", 2000, 2024), indent=2))
    # print(json.dumps(get_latest_cpi("US"), indent=2))
    # print(json.dumps(get_historical_average_cpi("US", 20), indent=2))
    # print(json.dumps(get_yearly_average_rate("AUD", "JPY", 2022), indent=2))
    # print(json.dumps(real_value("AUS", "JPN"), indent=2))
    # print(json.dumps(get_historical_average_rate("AUD", "JPY", 20), indent=2))
    # print(json.dumps(real_value_historical_average("AUS", "JPN", 20), indent=2))
    
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

    # Run this for your test cases
    debug_travel_value("AUS", "JPN")
    debug_travel_value("AUS", "GRC")
    debug_travel_value("AUS", "USA")
    debug_travel_value("AUS", "CHE")
    
    print(json.dumps(calculate_travel_value_index_corrected("AUS", "JPN", 20), indent=2))
    print(json.dumps(calculate_travel_value_index_corrected("AUS", "GRC", 20), indent=2))
    print(json.dumps(calculate_travel_value_index_corrected("AUS", "USA", 20), indent=2))
    print(json.dumps(calculate_travel_value_index_corrected("AUS", "CHE", 20), indent=2))
    
    print(json.dumps(calculate_travel_value_index("AUS", "JPN", 20), indent=2))
    print(json.dumps(calculate_travel_value_index("AUS", "GRC", 20), indent=2))
    print(json.dumps(calculate_travel_value_index("AUS", "USA", 20), indent=2))
    print(json.dumps(calculate_travel_value_index("AUS", "CHE", 20), indent=2))