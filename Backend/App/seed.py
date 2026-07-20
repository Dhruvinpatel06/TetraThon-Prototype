from .database import SessionLocal
from .models import Location, Crop
 
LOCATIONS = [
    {"name": "Vadodara", "state": "Gujarat", "latitude": 22.3072, "longitude": 73.1812},
    {"name": "Anand", "state": "Gujarat", "latitude": 22.5645, "longitude": 72.9289},
    {"name": "Rajkot", "state": "Gujarat", "latitude": 22.3039, "longitude": 70.8022},
    {"name": "Ahmedabad", "state": "Gujarat", "latitude": 23.0225, "longitude": 72.5714},
    {"name": "Surat", "state": "Gujarat", "latitude": 21.1702, "longitude": 72.8311},
]

CROPS = [
    {"name": "Cotton", "typical_duration_days": 180, "category": "cash_crop"},
    {"name": "Wheat", "typical_duration_days": 120, "category": "cereal"},
    {"name": "Groundnut", "typical_duration_days": 110, "category": "oilseed"},
    {"name": "Tomato", "typical_duration_days": 75, "category": "vegetable"},
]


def seed():
    db = SessionLocal()
    try:
        if db.query(Location).count() == 0:
            db.bulk_insert_mappings(Location, LOCATIONS)
        if db.query(Crop).count() == 0:
            db.bulk_insert_mappings(Crop, CROPS)
        db.commit()
        print(f"Seeded {db.query(Location).count()} locations, {db.query(Crop).count()} crops.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()