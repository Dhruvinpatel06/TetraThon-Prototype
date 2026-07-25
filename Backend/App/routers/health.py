from fastapi import APIRouter
from ..adapters.market_prices import get_price_adapter_status

router = APIRouter()


@router.get("/health")
def health():
    # Report adapter configuration/status without live API calls
    weather_source = "configured"
    
    try:
        price_source = get_price_adapter_status("Cotton", "Ahmedabad APMC")
    except Exception:
        price_source = "error"

    return {
        "status": "OK",
        "version": "1.0.0-phase1",
        "adapters": {
            "weather": weather_source,
            "prices": price_source
        }
    }
