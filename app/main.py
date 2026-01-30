from fastapi import FastAPI
import json
from app.services.fx import get_latest_rates, get_supported_currencies, get_historical_rates
from app.services.cpi import get_cpi_data, get_latest_cpi, get_cpi_historical

app = FastAPI()


@app.get("/")
async def root():
    return {"name": "Loukaniko",
            "description": "Travel value data API",
            "version": "v1", 
            }


if __name__ == "__main__":
    # print(json.dumps(get_latest_rates(), indent=2))
    print(json.dumps(get_supported_currencies(), indent=2))
    # print(json.dumps(get_historical_rates(), indent=2))
    # print(json.dumps(get_cpi_data("US", 2000, 2024), indent=2))
    # print(json.dumps(get_latest_cpi("US"), indent=2))
    # print(json.dumps(get_cpi_historical("US", 2000, 2024), indent=2))