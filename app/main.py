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
    print(json.dumps(get_latest_cpi("US"), indent=2))
    # print(json.dumps(get_historical_average_cpi("US", 20), indent=2))
    # print(json.dumps(get_yearly_average_rate("AUD", "JPY", 2022), indent=2))
    # print(json.dumps(real_value("AUS", "JPN"), indent=2))
    # print(json.dumps(get_historical_average_rate("AUD", "JPY", 20), indent=2))
    # print(json.dumps(real_value_historical_average("AUS", "JPN", 20), indent=2))

    
    # print(json.dumps(calculate_travel_value_index_corrected("AUS", "JPN", 20), indent=2))
    # print(json.dumps(calculate_travel_value_index_corrected("AUS", "GRC", 20), indent=2))
    # print(json.dumps(calculate_travel_value_index_corrected("AUS", "USA", 20), indent=2))
    # print(json.dumps(calculate_travel_value_index_corrected("AUS", "CHE", 20), indent=2))
