import datetime

LOCATION_WEATHER = {
    "Vadodara": {
        "temp_high": 40,
        "temp_low": 28,
        "rain_chances": [10, 15, 5, 20, 10, 5, 15],
        "humidity": 50,
        "wind_kph": 10
    },
    "Anand": {
        "temp_high": 38,
        "temp_low": 27,
        "rain_chances": [10, 60, 80, 20, 10, 15, 30],
        "humidity": 55,
        "wind_kph": 12
    },
    "Rajkot": {
        "temp_high": 42,
        "temp_low": 29,
        "rain_chances": [5, 5, 10, 10, 5, 5, 10],
        "humidity": 45,
        "wind_kph": 15
    },
    "Ahmedabad": {
        "temp_high": 41,
        "temp_low": 30,
        "rain_chances": [0, 0, 5, 10, 5, 0, 0],
        "humidity": 40,
        "wind_kph": 8
    },
    "Surat": {
        "temp_high": 35,
        "temp_low": 26,
        "rain_chances": [40, 50, 60, 45, 30, 40, 50],
        "humidity": 75,
        "wind_kph": 18
    }
}


def get_forecast(location: str) -> dict:
    """
    Returns a deterministic 7-day weather forecast for a given location.
    Raises ValueError if the location is unknown.
    """
    if not location:
        raise ValueError("Location name cannot be empty")

    # Case-insensitive search
    matched_location = next(
        (loc for loc in LOCATION_WEATHER if loc.lower() == location.strip().lower()),
        None
    )

    if not matched_location:
        raise ValueError(f"Unknown location: {location}")

    config = LOCATION_WEATHER[matched_location]
    forecast = []
    base_date = datetime.date.today()

    for i in range(1, 8):
        # Generate date starting from tomorrow (base_date + i days)
        forecast_date = base_date + datetime.timedelta(days=i)
        
        # Small deterministic adjustments per day for realism (wave pattern)
        day_offset = (i - 1) % 3 - 1  # -1, 0, 1
        
        forecast.append({
            "day": i,
            "date": forecast_date.isoformat(),
            "temp_high": config["temp_high"] + day_offset,
            "temp_low": config["temp_low"] + day_offset,
            "rain_chance": config["rain_chances"][i - 1],
            "humidity": min(100, max(0, config["humidity"] + day_offset * 3)),
            "wind_kph": max(0, config["wind_kph"] + day_offset)
        })

    return {
        "location": matched_location,
        "forecast": forecast
    }
