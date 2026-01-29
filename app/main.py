from fastapi import FastAPI
import json
from app.services.fx import get_latest_rates, get_supported_currencies, get_historical_rates

app = FastAPI()


@app.get("/")
async def root():
    return {"name": "Loukaniko",
            "description": "Travel value data API",
            "version": "v1", 
            }


if __name__ == "__main__":
    # print(json.dumps(get_latest_rates(), indent=2))
    # print(json.dumps(get_supported_currencies(), indent=2))
    print(json.dumps(get_historical_rates(), indent=2))