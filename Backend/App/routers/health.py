from fastapi import APIRouter
from ..adapters.market_prices import get_price_adapter_status

router = APIRouter()


@router.get("/health")
def health():
    return {
        "status": "OK",
        "version": "1.0.0-phase1",
        "adapters": {
            "weather": "configured",
            "prices": "configured"
        }
    }
