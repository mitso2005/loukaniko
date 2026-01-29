
from fastapi import APIRouter, Query
from app.services.fx import get_latest_rates, get_supported_currencies, get_historical_rates

router = APIRouter()

@router.get("/rates/latest")
def latest_rates(base: str = Query("EUR", description="Base currency code")):
    return get_latest_rates(base)


@router.get("/currencies")
def supported_currencies():
    return get_supported_currencies()

@router.get("/rates/{date_start}..{date_end}")
def historical_rates(date_start: str, date_end: str, base: str = Query("EUR", description="Base currency code")):
    return get_historical_rates(date_start, date_end, base)