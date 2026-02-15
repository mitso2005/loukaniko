from fastapi import FastAPI, Query, HTTPException
import json
from pathlib import Path

from app.services.fx import (
    get_latest_rate,
    get_supported_currencies,
    get_historical_average_rate,
    get_fx_stats,
)
from app.services.cpi import (
    get_latest_cpi,
    get_historical_average_cpi,
    get_available_countries,
    get_database_stats,
)
from app.logic.travel_cost import (
    calculate_travel_value_index_corrected,
    rank_countries_by_travel_value,
)
from app.utils.name_conversion import country_to_currency

# Constants
COUNTRIES_JSON_PATH = Path("app/data/countries.json")

app = FastAPI(
    title="Loukaniko Travel Value API",
    description="API for calculating travel value indices based on FX rates and CPI data",
    version="1.0.0",
)


# Helper functions
def load_countries_data():
    """Load and return countries data from JSON file."""
    with open(COUNTRIES_JSON_PATH, encoding="utf-8") as f:
        return json.load(f)


# ============================================================================
# Info Endpoints
# ============================================================================


@app.get("/")
async def root():
    """API information and health check."""
    return {
        "name": "Loukaniko",
        "description": "Travel value data API",
        "version": "1.0.0",
    }


@app.get("/stats")
async def get_all_stats():
    """Returns statistics about both FX and CPI databases."""
    try:
        return {
            "fx": get_fx_stats(),
            "cpi": get_database_stats(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")


# ============================================================================
# Travel Value Endpoints
# ============================================================================


@app.get("/travel-value-rankings/{country_code}")
async def get_travel_value_rankings(country_code: str):
    """Get ranked list of travel destinations by value from a base country."""
    try:
        results = rank_countries_by_travel_value(country_code)
        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"No travel value data found for country: {country_code}",
            )
        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating travel value rankings: {str(e)}",
        )


@app.get("/travel-value-index/{base_country_code}/{target_country_code}")
async def get_travel_value_index(
    base_country_code: str,
    target_country_code: str,
    years: int = Query(20, description="Number of historical years to compare"),
):
    """Calculate the travel value index between two countries."""
    try:
        return calculate_travel_value_index_corrected(
            base_country_code, target_country_code, years
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating travel value index: {str(e)}",
        )


# ============================================================================
# Countries Endpoints
# ============================================================================


@app.get("/countries")
async def get_countries():
    """Returns a simple list of country codes and names."""
    try:
        data = load_countries_data()
        countries_list = data.get("countries", [])
        return [
            {
                "countryCode": country["countryCode"],
                "country": country["country"],
            }
            for country in countries_list
        ]
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Countries data file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving countries: {str(e)}")


@app.get("/countries/details")
async def get_countries_details():
    """Returns complete country information including currency details."""
    try:
        return load_countries_data()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Countries data file not found")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving country details: {str(e)}"
        )


@app.get("/countries/available")
async def get_available_countries_endpoint():
    """
    Returns countries with both CPI data AND supported currency in FX database.
    Only includes the intersection of countries with CPI data and available FX rates.
    """
    try:
        cpi_countries = get_available_countries()
        supported_currencies = get_supported_currencies()

        available_countries = [
            country
            for country in cpi_countries
            if (country_code := country.get("code"))
            and (currency := country_to_currency(country_code))
            and currency in supported_currencies
        ]

        return available_countries
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving available countries: {str(e)}"
        )


# ============================================================================
# Currency Endpoints
# ============================================================================


@app.get("/currencies")
async def get_currencies():
    """Returns list of supported currencies."""
    try:
        return get_supported_currencies()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving currencies: {str(e)}")

@app.get("/currencies")
async def get_currencies():
    """Returns list of supported currencies."""
    try:
        return get_supported_currencies()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving currencies: {str(e)}")


# ============================================================================
# FX Rate Endpoints
# ============================================================================


@app.get("/fx/latest/{base_currency}/{target_currency}")
async def get_fx_rate(base_currency: str, target_currency: str):
    """Returns the latest FX rate between two currencies."""
    try:
        rate = get_latest_rate(base_currency.upper(), target_currency.upper())
        if rate is None:
            raise HTTPException(
                status_code=404,
                detail=f"FX rate not found for {base_currency}/{target_currency}",
            )
        return {"rate": rate}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving FX rate: {str(e)}")


@app.get("/fx/historical/{base_currency}/{target_currency}")
async def get_fx_historical(
    base_currency: str,
    target_currency: str,
    years: int = Query(20, description="Number of years to average"),
):
    """Returns the historical average FX rate over the specified number of years."""
    try:
        rate = get_historical_average_rate(
            base_currency.upper(), target_currency.upper(), years
        )
        if rate is None:
            raise HTTPException(
                status_code=404,
                detail=f"Historical FX data not found for {base_currency}/{target_currency}",
            )
        return {
            "base_currency": base_currency.upper(),
            "target_currency": target_currency.upper(),
            "years": years,
            "average_rate": rate,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving historical FX rate: {str(e)}"
        )


# ============================================================================
# CPI Endpoints
# ============================================================================


@app.get("/cpi/latest/{country_code}")
async def get_cpi_latest(country_code: str):
    """Returns the latest CPI for a given country."""
    try:
        cpi = get_latest_cpi(country_code.upper())
        if cpi is None:
            raise HTTPException(
                status_code=404, detail=f"CPI data not found for country: {country_code}"
            )
        return {"cpi": cpi}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving CPI: {str(e)}")


@app.get("/cpi/historical/{country_code}")
async def get_cpi_historical(
    country_code: str,
    years: int = Query(20, description="Number of years to average"),
):
    """Returns the historical average CPI for a country over the specified number of years."""
    try:
        cpi = get_historical_average_cpi(country_code.upper(), years)
        if cpi is None:
            raise HTTPException(
                status_code=404,
                detail=f"Historical CPI data not found for country: {country_code}",
            )
        return {
            "country_code": country_code.upper(),
            "years": years,
            "average_cpi": cpi,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving historical CPI: {str(e)}"
        )