from fastapi import FastAPI, APIRouter, Query
import json
import os
from pathlib import Path
from app.services.fx import (
    get_latest_rate, 
    get_supported_currencies, 
    get_year_average_rate, 
    get_historical_average_rate,
    get_fx_stats,
    get_latest_date
)
from app.services.cpi import (
    get_latest_cpi, 
    get_historical_average_cpi,
    get_cpi_for_year,
    get_available_countries,
    get_database_stats
)
from app.logic.travel_cost import calculate_travel_value_index, calculate_travel_value_index_corrected, rank_countries_by_travel_value
from app.utils.name_conversion import country_to_currency

app = FastAPI()


@app.get("/")
async def root():
    return {"name": "Loukaniko",
            "description": "Travel value data API",
            "version": "v1", 
            }

@app.get("/currencies")
def currencies_endpoint():
    return get_supported_currencies()

@app.get("/travel-value-rankings/{country_code}")
async def get_travel_value_index_ranked(country_code: str):
    return rank_countries_by_travel_value(country_code)

@app.get("/travel-value-index/{base_country_code}/{target_country_code}")
async def get_travel_value_index(base_country_code: str, target_country_code: str, years: int = 20):
    """
    Calculates the travel value index between a base and target country.
    """
    return calculate_travel_value_index_corrected(base_country_code, target_country_code, years)

@app.get("/fx/latest/{base_currency}/{target_currency}")
async def get_fx_rate(base_currency: str, target_currency: str):
    """
    Returns the latest FX rate between two currencies.
    """
    return {"rate": get_latest_rate(base_currency.upper(), target_currency.upper())}

@app.get("/cpi/latest/{country_code}")
async def get_cpi(country_code: str):
    """
    Returns the latest CPI for a given country.
    """
    return {"cpi": get_latest_cpi(country_code.upper())}

@app.get("/countries")
async def get_countries():
    """
    Returns a simple list of country codes and names.
    """
    countries_path = Path("app/data/countries.json")
    with open(countries_path, encoding="utf-8") as f:
        data = json.load(f)
    
    countries_list = data.get("countries", [])
    return [
        {
            "countryCode": country["countryCode"],
            "country": country["country"]
        }
        for country in countries_list
    ]

@app.get("/countries/details")
async def get_countries_details():
    """
    Returns complete country information including currency details.
    """
    countries_path = Path("app/data/countries.json")
    with open(countries_path, encoding="utf-8") as f:
        data = json.load(f)
    return data

@app.get("/countries/available")
async def get_countries_with_cpi_data():
    """
    Returns countries that have CPI data available in the database.
    """
    return get_available_countries()

@app.get("/fx/historical/{base_currency}/{target_currency}")
async def get_fx_historical(base_currency: str, target_currency: str, years: int = Query(20, description="Number of years to average")):
    """
    Returns the historical average FX rate over the specified number of years.
    """
    rate = get_historical_average_rate(base_currency.upper(), target_currency.upper(), years)
    return {
        "base_currency": base_currency.upper(),
        "target_currency": target_currency.upper(),
        "years": years,
        "average_rate": rate
    }

@app.get("/fx/year/{base_currency}/{target_currency}/{year}")
async def get_fx_year(base_currency: str, target_currency: str, year: int):
    """
    Returns the average FX rate for a specific year.
    """
    rate = get_year_average_rate(base_currency.upper(), target_currency.upper(), year)
    return {
        "base_currency": base_currency.upper(),
        "target_currency": target_currency.upper(),
        "year": year,
        "average_rate": rate
    }

@app.get("/cpi/historical/{country_code}")
async def get_cpi_historical(country_code: str, years: int = Query(20, description="Number of years to average")):
    """
    Returns the historical average CPI for a country over the specified number of years.
    """
    cpi = get_historical_average_cpi(country_code.upper(), years)
    return {
        "country_code": country_code.upper(),
        "years": years,
        "average_cpi": cpi
    }

@app.get("/cpi/year/{country_code}/{year}")
async def get_cpi_for_specific_year(country_code: str, year: int):
    """
    Returns the CPI for a specific country and year.
    """
    cpi = get_cpi_for_year(country_code.upper(), year)
    return {
        "country_code": country_code.upper(),
        "year": year,
        "cpi": cpi
    }

@app.get("/stats")
async def get_all_stats():
    """
    Returns statistics about both FX and CPI databases.
    """
    return {
        "fx": get_fx_stats(),
        "cpi": get_database_stats()
    }

@app.get("/stats/fx")
async def get_fx_statistics():
    """
    Returns statistics about the FX rates database.
    """
    return get_fx_stats()

@app.get("/stats/cpi")
async def get_cpi_statistics():
    """
    Returns statistics about the CPI database.
    """
    return get_database_stats()

@app.get("/fx/latest-date")
async def get_fx_latest_date():
    """
    Returns the most recent date with FX data available.
    """
    return {"latest_date": get_latest_date()}

if __name__ == "__main__":
    print(json.dumps(rank_countries_by_travel_value("AUS", 20, 20), indent=2))