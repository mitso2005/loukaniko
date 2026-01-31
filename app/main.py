from fastapi import FastAPI
import json
from app.services.fx import get_latest_rate, get_supported_currencies, get_year_average_rate, get_historical_average_rate
from app.services.cpi import get_latest_cpi
from app.logic.travel_cost import calculate_travel_value_index, calculate_travel_value_index_corrected, rank_countries_by_travel_value
from app.utils.name_conversion import country_to_currency
from app.services.fx import get_latest_rate, get_supported_currencies, get_year_average_rate, get_historical_average_rate

app = FastAPI()


@app.get("/")
async def root():
    return {"name": "Loukaniko",
            "description": "Travel value data API",
            "version": "v1", 
            }


if __name__ == "__main__":
    print(json.dumps(rank_countries_by_travel_value("AUS", 20, 20), indent=2))
