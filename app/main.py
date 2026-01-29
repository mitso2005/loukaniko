from fastapi import FastAPI
import json
from app.services.fx import get_latest_rates

app = FastAPI()


@app.get("/")
async def root():
    return {"name": "Loukaniko",
            "description": "Travel value data API",
            "version": "v1", 
            }


if __name__ == "__main__":
    print(json.dumps(get_latest_rates(), indent=2))