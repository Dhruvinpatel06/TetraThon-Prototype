import csv
import logging
from pathlib import Path
import httpx
from .config import AGMARKNET_API_KEY, AGMARKNET_BASE_URL, AGMARKNET_TIMEOUT

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CSV_PATH = BASE_DIR / "data" / "mandi_prices.csv"

MARKET_IDS = {
    "Ahmedabad APMC": "GJ001",
    "Vadodara APMC": "GJ002",
    "Surat APMC": "GJ003",
    "Rajkot APMC": "GJ004",
    "Anand APMC": "GJ005",
}

import time

_live_prices_cache = {}
_csv_prices_cache = {}
_failed_fetch_cache = {}  # (crop, market) -> timestamp of last failure
FAILURE_CACHE_TTL = 60  # seconds to cache a failed API fetch before retrying


def _fetch_live_prices(crop: str, market: str) -> list[dict] | None:
    """Attempt to fetch prices from data.gov.in API. Returns None on failure."""
    if not AGMARKNET_API_KEY:
        logger.warning(f"Market Prices: No AGMARKNET_API_KEY set, skipping live fetch for {crop} at {market}")
        return None
    
    market_id = MARKET_IDS.get(market)
    if not market_id:
        logger.warning(f"Market Prices: Unknown market ID for {market}, skipping live fetch")
        return None

    cache_key = (crop, market)
    if cache_key in _live_prices_cache:
        return _live_prices_cache[cache_key]

    # Check if a recent failure occurred to avoid repeated blocking timeouts
    last_failure = _failed_fetch_cache.get(cache_key)
    if last_failure and (time.time() - last_failure < FAILURE_CACHE_TTL):
        return None
    
    try:
        import ssl
        ssl_ctx = ssl.create_default_context()
        try:
            ssl_ctx.minimum_version = ssl.TLSVersion.TLS1_2
            ssl_ctx.maximum_version = ssl.TLSVersion.TLS1_2
        except Exception:
            pass

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        with httpx.Client(timeout=AGMARKNET_TIMEOUT, headers=headers, verify=ssl_ctx) as client:
            resp = client.get(AGMARKNET_BASE_URL, params={
                "api-key": AGMARKNET_API_KEY,
                "format": "json",
                "filters[commodity]": crop,
                "filters[market]": market,
                "limit": 90
            })
            resp.raise_for_status()
            data = resp.json()
            
            records = []
            for record in data.get("records", []):
                price_val = float(record.get("modal_price", 0))
                records.append({
                    "date": record.get("date", ""),
                    "price": price_val,
                    "price_per_quintal": price_val
                })
            
            records.sort(key=lambda x: x["date"])
            if records:
                _live_prices_cache[cache_key] = records
                return records
    except Exception as exc:
        logger.warning(f"Market Prices API call failed for {crop} at {market}: {exc}. Falling back to CSV data.")
        _failed_fetch_cache[cache_key] = time.time()
        return None

    _failed_fetch_cache[cache_key] = time.time()
    return None


def load_prices(crop: str, market: str) -> list[dict]:
    """
    Returns price series for crop at market. Tries live API first, falls back to CSV.
    """
    crop = crop.strip().capitalize() if crop else ""
    market = market.strip() if market else ""
    
    cache_key = (crop, market)
    
    # Try live API first
    live_data = _fetch_live_prices(crop, market)
    if live_data:
        logger.info(f"Market Prices: live data used for {crop} at {market}")
        return live_data
    
    # Fallback to CSV (original Phase 0 logic)
    logger.info(f"Market Prices: fallback to CSV for {crop} at {market}")
    if cache_key in _csv_prices_cache:
        return _csv_prices_cache[cache_key]
    
    if not CSV_PATH.exists():
        return []
    
    if not _csv_prices_cache:
        with open(CSV_PATH, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row["crop"].strip().capitalize(), row["market"].strip())
                price_val = float(row["price_per_quintal"])
                if key not in _csv_prices_cache:
                    _csv_prices_cache[key] = []
                _csv_prices_cache[key].append({
                    "date": row["date"],
                    "price": price_val,
                    "price_per_quintal": price_val
                })
        for key in _csv_prices_cache:
            _csv_prices_cache[key].sort(key=lambda x: x["date"])
    
    return _csv_prices_cache.get(cache_key, [])


def get_latest_price(crop: str, market: str) -> float:
    """
    Returns the latest price for the crop at the given market.
    Evaluation date is 14 days before the end of the series.
    """
    prices = load_prices(crop, market)
    if not prices:
        return 0.0
    target_idx = max(0, len(prices) - 15)
    return prices[target_idx]["price"]


def get_future_price(crop: str, market: str, days_from_now: int) -> float:
    """
    Returns the price for the crop at the given market `days_from_now` from evaluation date.
    """
    prices = load_prices(crop, market)
    if not prices:
        return 0.0
    target_idx = max(0, len(prices) - 15)
    future_idx = target_idx + days_from_now
    if future_idx < len(prices):
        return prices[future_idx]["price"]
    else:
        return prices[-1]["price"]


def get_price_adapter_status(crop: str = "Cotton", market: str = "Ahmedabad APMC") -> str:
    """Returns 'live' if prices were fetched from live API, otherwise 'mock'."""
    prices = load_prices(crop, market)
    cache_key = (crop.strip().capitalize(), market.strip())
    if cache_key in _live_prices_cache:
        return "live"
    return "mock"

