import csv
import datetime
from pathlib import Path
from .transport import MARKETS, haversine, transport_cost
from .spoilage import compute_spoilage

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CSV_PATH = BASE_DIR / "data" / "mandi_prices.csv"

# Module-level cache: key is (crop, market), value is list of {"date": date, "price": price, "price_per_quintal": price}
_prices_cache = {}

def load_prices(crop: str, market: str) -> list[dict]:
    """
    Reads the mandi_prices.csv file, filters by the specified crop and market,
    and returns a list of dictionaries with 'date' and 'price' / 'price_per_quintal'
    sorted by date ascending. Uses module-level caching for performance.
    """
    # Normalize inputs for case-insensitivity
    crop = crop.strip().capitalize() if crop else ""
    market = market.strip() if market else ""
    
    cache_key = (crop, market)
    if cache_key in _prices_cache:
        return _prices_cache[cache_key]
        
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV file not found at {CSV_PATH}")
        
    # If cache is empty, load everything in one pass to populate the cache
    if not _prices_cache:
        with open(CSV_PATH, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row["crop"].strip().capitalize(), row["market"].strip())
                price_val = float(row["price_per_quintal"])
                if key not in _prices_cache:
                    _prices_cache[key] = []
                _prices_cache[key].append({
                    "date": row["date"],
                    "price": price_val,
                    "price_per_quintal": price_val
                })
        
        # Sort each list by date
        for key in _prices_cache:
            _prices_cache[key].sort(key=lambda x: x["date"])
            
    # Return the cached list, default to empty list if not found
    return _prices_cache.get(cache_key, [])

def get_latest_price(crop: str, market: str) -> float:
    """
    Returns the latest price for the crop at the given market.
    We define the latest evaluation date as 14 days before the end of the series
    so we can compute future lookup prices.
    """
    prices = load_prices(crop, market)
    if not prices:
        return 0.0
    # Use 14 days before the last element of the dataset as the 'current' reference point
    target_idx = max(0, len(prices) - 15)
    return prices[target_idx]["price"]

def get_future_price(crop: str, market: str, days_from_now: int) -> float:
    """
    Returns the price for the crop at the given market `days_from_now` from the evaluation date.
    If out of bounds, falls back to the latest available price in the series.
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

def find_closest_market(lat: float, lng: float) -> str:
    """
    Finds the name of the closest market by distance.
    """
    closest_m = None
    min_dist = float("inf")
    for m in MARKETS:
        dist = haversine(lat, lng, m["latitude"], m["longitude"])
        if dist < min_dist:
            min_dist = dist
            closest_m = m["name"]
    return closest_m

def generate_recommendation(crop: str, quantity: float, storage: str, lat: float, lng: float) -> dict:
    """
    Compares 3 options (Sell Now, Store, Transport) and returns the optimal recommendation.
    """
    crop = crop.strip().capitalize() if crop else ""
    quantity = max(0.0, quantity)
    
    # 1. Find nearest market
    nearest_market_name = find_closest_market(lat, lng)
    
    # Get all transport costs to markets
    t_costs = transport_cost(lat, lng, quantity)
    t_costs_dict = {item["market"]: item for item in t_costs}
    
    # Nearest market transport details
    nearest_t_detail = t_costs_dict[nearest_market_name]
    
    # ------------------
    # Option 1: Sell Now
    # ------------------
    sell_now_price = get_latest_price(crop, nearest_market_name)
    sell_now_revenue = sell_now_price * quantity
    sell_now_tc = nearest_t_detail["transport_cost"]
    sell_now_net = sell_now_revenue - sell_now_tc
    
    # ------------------
    # Option 2: Store (14 days)
    # ------------------
    store_days = 14
    future_price = get_future_price(crop, nearest_market_name, store_days)
    future_revenue = future_price * quantity
    
    # Calculate spoilage
    spoilage_res = compute_spoilage(crop, storage, store_days, future_revenue)
    spoilage_loss = spoilage_res["total_loss"]
    
    # Storage rates: warehouse ₹2/q/day, cold_storage ₹5/q/day, open/others ₹0/q/day
    storage_rate = 0.0
    storage_lower = storage.strip().lower() if storage else ""
    if storage_lower == "warehouse":
        storage_rate = 2.0
    elif storage_lower == "cold_storage":
        storage_rate = 5.0
        
    storage_cost_val = store_days * storage_rate * quantity
    store_net = future_revenue - spoilage_loss - storage_cost_val
    
    # ------------------
    # Option 3: Transport to Best Market
    # ------------------
    best_transport_market = None
    best_transport_net = -float("inf")
    best_transport_price = 0.0
    best_transport_tc = 0.0
    best_transport_dist = 0.0
    
    for m in MARKETS:
        m_name = m["name"]
        m_price = get_latest_price(crop, m_name)
        m_tc = t_costs_dict[m_name]["transport_cost"]
        m_net = (m_price * quantity) - m_tc
        if m_net > best_transport_net:
            best_transport_net = m_net
            best_transport_market = m_name
            best_transport_price = m_price
            best_transport_tc = m_tc
            best_transport_dist = t_costs_dict[m_name]["distance_km"]
            
    # ------------------
    # Decision Engine Comparison
    # Prefer Sell Now in case of ties: Sell Now >= Store >= Transport
    # ------------------
    if sell_now_net >= store_net and sell_now_net >= best_transport_net:
        rec_type = "sell_now"
        option_label = "Sell Now"
        expected_return = sell_now_net
    elif store_net >= best_transport_net:
        rec_type = "store"
        option_label = "Store"
        expected_return = store_net
    else:
        rec_type = "transport"
        option_label = "Transport to Best Market"
        expected_return = best_transport_net
        
    expected_return_per_q = (expected_return / quantity) if quantity > 0 else 0.0
    
    # Reason text construction
    if rec_type == "sell_now":
        reason = f"Selling locally at {nearest_market_name} yields the highest expected net return of ₹{round(sell_now_net, 2):,}."
    elif rec_type == "store":
        diff = store_net - sell_now_net
        reason = f"Storing {crop} for {store_days} days yields an expected return of ₹{round(store_net, 2):,} (after storage cost and spoilage) — ₹{round(diff, 2):,} more than selling now."
    else:
        diff = best_transport_net - sell_now_net
        reason = f"Transporting to {best_transport_market} yields an expected return of ₹{round(best_transport_net, 2):,} — ₹{round(diff, 2):,} more than selling locally."
        
    return {
        "recommendation": rec_type,
        "option_label": option_label,
        "expected_return": round(expected_return, 2),
        "expected_return_per_quintal": round(expected_return_per_q, 2),
        "details": {
            "sell_now": {
                "market": nearest_market_name,
                "price_per_quintal": round(sell_now_price, 2),
                "transport_cost": round(sell_now_tc, 2),
                "net_return": round(sell_now_net, 2),
                "distance_km": round(nearest_t_detail["distance_km"], 2)
            },
            "store": {
                "market": nearest_market_name,
                "store_days": store_days,
                "storage": storage,
                "spoilage_loss": round(spoilage_loss, 2),
                "storage_cost": round(storage_cost_val, 2),
                "future_price_per_quintal": round(future_price, 2),
                "net_return": round(store_net, 2)
            },
            "transport": {
                "market": best_transport_market,
                "price_per_quintal": round(best_transport_price, 2),
                "transport_cost": round(best_transport_tc, 2),
                "distance_km": round(best_transport_dist, 2),
                "net_return": round(best_transport_net, 2)
            }
        },
        "reason": reason
    }
