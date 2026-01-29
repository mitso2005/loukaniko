
from fastapi import APIRouter, Query
from app.services.fx import get_latest_rates, get_supported_currencies, get_historical_rates
from app.services.cpi import get_cpi_data

router = APIRouter()

@router.get("/rates/latest")
def latest_rates(base: str = Query("EUR", description="Base currency code")):
    return get_latest_rates(base)

@router.get("/currencies")
def supported_currencies():
    return get_supported_currencies()

@router.get("/rates/historical/{date_start}:{date_end}")
def historical_rates(date_start: str, date_end: str, base: str = Query("EUR", description="Base currency code")):
    return get_historical_rates(date_start, date_end, base)

@router.get("/cpi/{country_code}..{year_start}:{year_end}")
def cpi(country_code: str, year_start: int = Query(2000, description="Start year"), year_end: int = Query(2024, description="End year")):
    return get_cpi_data(country_code, year_start, year_end)