from fastapi import FastAPI, APIRouter, Query, HTTPException
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

@app.get("/travel-value-rankings/{country_code}")
async def get_travel_value_index_ranked(country_code: str):
    try:
        results = rank_countries_by_travel_value(country_code)
        if not results:
            raise HTTPException(status_code=404, detail=f"No travel value data found for country: {country_code}")
        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating travel value rankings: {str(e)}")

@app.get("/travel-value-index/{base_country_code}/{target_country_code}")
async def get_travel_value_index(base_country_code: str, target_country_code: str, years: int = 20):
    """
    Calculates the travel value index between a base and target country.
    """
    try:
        result = calculate_travel_value_index_corrected(base_country_code, target_country_code, years)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating travel value index: {str(e)}")

@app.get("/countries/available")
async def get_countries_with_cpi_and_fx_data():
    """
    Returns countries that have both CPI data AND supported currency in FX database.
    Only includes the intersection of countries with CPI data and currencies available in FX rates.
    """
    try:
        # Get countries with CPI data
        cpi_countries = get_available_countries()
        
        # Get supported currencies
        supported_currencies = get_supported_currencies()
        
        # Filter to only include countries whose currency is supported
        available_countries = []
        for country in cpi_countries:
            country_code = country.get('code')
            if country_code:
                currency = country_to_currency(country_code)
                if currency and currency in supported_currencies:
                    available_countries.append(country)
        
        return available_countries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving available countries: {str(e)}")

@app.get("/currencies")
def currencies_endpoint():
    try:
        return get_supported_currencies()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving currencies: {str(e)}")

@app.get("/countries")
async def get_countries():
    """
    Returns a simple list of country codes and names.
    """
    try:
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
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Countries data file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving countries: {str(e)}")

@app.get("/countries/details")
async def get_countries_details():
    """
    Returns complete country information including currency details.
    """
    try:
        countries_path = Path("app/data/countries.json")
        with open(countries_path, encoding="utf-8") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Countries data file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving country details: {str(e)}")

@app.get("/fx/latest/{base_currency}/{target_currency}")
async def get_fx_rate(base_currency: str, target_currency: str):
    """
    Returns the latest FX rate between two currencies.
    """
    try:
        rate = get_latest_rate(base_currency.upper(), target_currency.upper())
        if rate is None:
            raise HTTPException(status_code=404, detail=f"FX rate not found for {base_currency}/{target_currency}")
        return {"rate": rate}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving FX rate: {str(e)}")

@app.get("/cpi/latest/{country_code}")
async def get_cpi(country_code: str):
    """
    Returns the latest CPI for a given country.
    """
    try:
        cpi = get_latest_cpi(country_code.upper())
        if cpi is None:
            raise HTTPException(status_code=404, detail=f"CPI data not found for country: {country_code}")
        return {"cpi": cpi}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving CPI: {str(e)}")


@app.get("/fx/historical/{base_currency}/{target_currency}")
async def get_fx_historical(base_currency: str, target_currency: str, years: int = Query(20, description="Number of years to average")):
    """
    Returns the historical average FX rate over the specified number of years.
    """
    try:
        rate = get_historical_average_rate(base_currency.upper(), target_currency.upper(), years)
        if rate is None:
            raise HTTPException(status_code=404, detail=f"Historical FX data not found for {base_currency}/{target_currency}")
        return {
            "base_currency": base_currency.upper(),
            "target_currency": target_currency.upper(),
            "years": years,
            "average_rate": rate
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving historical FX rate: {str(e)}")

@app.get("/cpi/historical/{country_code}")
async def get_cpi_historical(country_code: str, years: int = Query(20, description="Number of years to average")):
    """
    Returns the historical average CPI for a country over the specified number of years.
    """
    try:
        cpi = get_historical_average_cpi(country_code.upper(), years)
        if cpi is None:
            raise HTTPException(status_code=404, detail=f"Historical CPI data not found for country: {country_code}")
        return {
            "country_code": country_code.upper(),
            "years": years,
            "average_cpi": cpi
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving historical CPI: {str(e)}")

@app.get("/stats")
async def get_all_stats():
    """
    Returns statistics about both FX and CPI databases.
    """
    try:
        return {
            "fx": get_fx_stats(),
            "cpi": get_database_stats()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")