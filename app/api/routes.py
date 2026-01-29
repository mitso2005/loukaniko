from fastapi import APIRouter, Query
from app.services.fx import get_latest_rates

router = APIRouter()

@router.get("/rates/latest")
def latest_rates(base: str = Query("EUR", description="Base currency code")):
    return get_latest_rates(base)