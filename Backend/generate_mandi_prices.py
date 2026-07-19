import csv
import datetime
import os
import random

def generate_prices():
    start_date = datetime.date(2026, 1, 1)
    days_count = 90
    
    crops = ["Cotton", "Wheat", "Groundnut", "Tomato"]
    markets = ["Ahmedabad APMC", "Vadodara APMC", "Surat APMC", "Rajkot APMC", "Anand APMC"]
    
    # Tuned trends so that Store and Transport sometimes win
    crop_configs = {
        "Cotton": {"base": 6500, "trend": 35.0, "var": 50, "min": 6000, "max": 9500},
        "Wheat": {"base": 2300, "trend": 45.0, "var": 20, "min": 2200, "max": 6500},
        "Groundnut": {"base": 5800, "trend": 30.0, "var": 40, "min": 5500, "max": 8500},
        "Tomato": {"base": 1500, "trend": 5.0, "var": 30, "min": 1200, "max": 2800}
    }
    
    # We introduce higher variance offsets between markets to make Transport win sometimes
    market_offsets = {
        "Ahmedabad APMC": 400,
        "Vadodara APMC": -200,
        "Surat APMC": 600,
        "Rajkot APMC": 200,
        "Anand APMC": 0
    }
    
    # We want to be deterministic, so we seed the generator
    random.seed(42)
    
    rows = []
    
    for d_idx in range(days_count):
        current_date = start_date + datetime.timedelta(days=d_idx)
        date_str = current_date.strftime("%Y-%m-%d")
        
        for crop in crops:
            cfg = crop_configs[crop]
            for market in markets:
                offset = market_offsets[market]
                
                # Base price with trend and market offset
                price = cfg["base"] + d_idx * cfg["trend"] + offset
                
                # Add daily variation
                noise = random.randint(-cfg["var"], cfg["var"])
                price += noise
                
                # Clamp within boundaries
                price = max(cfg["min"], min(cfg["max"], price))
                
                rows.append({
                    "date": date_str,
                    "crop": crop,
                    "market": market,
                    "price_per_quintal": int(price)
                })
                
    output_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "mandi_prices.csv")
    
    with open(output_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "crop", "market", "price_per_quintal"])
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"Generated {len(rows)} price records in {output_file}")

if __name__ == "__main__":
    generate_prices()
