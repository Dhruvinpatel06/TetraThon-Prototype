import math

MARKETS = [
    {"name": "Ahmedabad APMC", "latitude": 23.0225, "longitude": 72.5714},
    {"name": "Vadodara APMC", "latitude": 22.3072, "longitude": 73.1812},
    {"name": "Surat APMC", "latitude": 21.1702, "longitude": 72.8311},
    {"name": "Rajkot APMC", "latitude": 22.3039, "longitude": 70.8022},
    {"name": "Anand APMC", "latitude": 22.5645, "longitude": 72.9289},
]

def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculates the great-circle distance between two points on the Earth
    in kilometers using the Haversine formula.
    """
    R = 6371.0  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lng1_rad = math.radians(lng1)
    lat2_rad = math.radians(lat2)
    lng2_rad = math.radians(lng2)
    
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def transport_cost(lat: float, lng: float, quantity: float) -> list[dict]:
    """
    Computes transport cost to all 5 markets from a given coordinate.
    Cost per km per quintal is ₹5, with a minimum charge of ₹500.
    """
    # Normalize input quantity to be non-negative
    quantity = max(0.0, quantity)
    
    results = []
    for m in MARKETS:
        dist = haversine(lat, lng, m["latitude"], m["longitude"])
        
        # Calculate raw transport cost
        raw_cost = dist * 5.0 * quantity
        
        # Apply minimum charge of ₹500
        cost = max(500.0, raw_cost)
        
        results.append({
            "market": m["name"],
            "distance_km": round(dist, 2),
            "transport_cost": round(cost, 2)
        })
        
    return results
