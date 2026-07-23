import datetime
import logging
import httpx
from .config import OPENWEATHER_API_KEY, OPENWEATHER_BASE_URL, OPENWEATHER_TIMEOUT

logger = logging.getLogger(__name__)

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

LOCATION_COORDS = {
    "Ahmedabad": {"lat": 23.0225, "lon": 72.5714},
    "Vadodara": {"lat": 22.3072, "lon": 73.1812},
    "Surat": {"lat": 21.1702, "lon": 72.8311},
    "Rajkot": {"lat": 22.3039, "lon": 70.8022},
    "Anand": {"lat": 22.5645, "lon": 72.9289},
}


def _fetch_live_forecast(location: str) -> dict | None:
    """Attempt to fetch 7-day forecast from OpenWeatherMap. Returns None on failure."""
    if not OPENWEATHER_API_KEY:
        logger.warning(f"Weather: No OPENWEATHER_API_KEY set, skipping live fetch for {location}")
        return None
    
    coords = LOCATION_COORDS.get(location)
    if not coords:
        logger.warning(f"Weather: No coordinates for {location}, skipping live fetch")
        return None
    
    try:
        with httpx.Client(timeout=OPENWEATHER_TIMEOUT) as client:
            resp = client.get(OPENWEATHER_BASE_URL, params={
                "lat": coords["lat"],
                "lon": coords["lon"],
                "appid": OPENWEATHER_API_KEY,
                "units": "metric"
            })
            resp.raise_for_status()
            data = resp.json()
            
            forecast = _parse_owm_forecast(data)
            if forecast:
                return {"location": location, "forecast": forecast, "source": "live"}
    except Exception as exc:
        logger.warning(f"Weather API call failed for {location}: {exc}. Falling back to mock data.")
        return None
    return None


def _parse_owm_forecast(data: dict) -> list[dict]:
    """Convert OpenWeatherMap 3-hour forecast blocks into daily summaries."""
    daily = {}
    for item in data.get("list", []):
        date = item["dt_txt"].split(" ")[0]
        if date not in daily:
            daily[date] = {
                "temps": [], "humidity": [], "wind": [], "rain": []
            }
        daily[date]["temps"].append(item["main"]["temp"])
        daily[date]["humidity"].append(item["main"]["humidity"])
        daily[date]["wind"].append(item["wind"]["speed"] * 3.6)  # m/s to kph
        pop = item.get("pop", 0) * 100
        daily[date]["rain"].append(pop)
    
    forecast = []
    for i, (date, vals) in enumerate(sorted(daily.items())[:7], 1):
        forecast.append({
            "day": i,
            "date": date,
            "temp_high": round(max(vals["temps"])),
            "temp_low": round(min(vals["temps"])),
            "rain_chance": round(sum(vals["rain"]) / len(vals["rain"])),
            "humidity": round(sum(vals["humidity"]) / len(vals["humidity"])),
            "wind_kph": round(sum(vals["wind"]) / len(vals["wind"]))
        })

    # Ensure output always has 7 days by projecting remaining days if needed
    if forecast:
        last_date = datetime.date.fromisoformat(forecast[-1]["date"])
        while len(forecast) < 7:
            i = len(forecast) + 1
            last_date += datetime.timedelta(days=1)
            last_val = forecast[-1]
            forecast.append({
                "day": i,
                "date": last_date.isoformat(),
                "temp_high": last_val["temp_high"],
                "temp_low": last_val["temp_low"],
                "rain_chance": last_val["rain_chance"],
                "humidity": last_val["humidity"],
                "wind_kph": last_val["wind_kph"]
            })
    return forecast


def get_forecast(location: str) -> dict:
    """
    Returns 7-day weather forecast. Attempts live API first, falls back to mock.
    """
    if not location:
        raise ValueError("Location name cannot be empty")
    
    matched_location = next(
        (loc for loc in LOCATION_WEATHER if loc.lower() == location.strip().lower()),
        None
    )
    if not matched_location:
        raise ValueError(f"Unknown location: {location}")
    
    # Attempt live API
    live_result = _fetch_live_forecast(matched_location)
    if live_result:
        logger.info(f"Weather: live data used for {matched_location}")
        return live_result
    
    # Fallback to deterministic mock
    logger.info(f"Weather: fallback to mock for {matched_location}")
    return _get_mock_forecast(matched_location)


def _get_mock_forecast(location: str) -> dict:
    """Original deterministic mock forecast (unchanged from Phase 0)."""
    config = LOCATION_WEATHER[location]
    forecast = []
    base_date = datetime.date.today()
    for i in range(1, 8):
        forecast_date = base_date + datetime.timedelta(days=i)
        day_offset = (i - 1) % 3 - 1
        forecast.append({
            "day": i,
            "date": forecast_date.isoformat(),
            "temp_high": config["temp_high"] + day_offset,
            "temp_low": config["temp_low"] + day_offset,
            "rain_chance": config["rain_chances"][i - 1],
            "humidity": min(100, max(0, config["humidity"] + day_offset * 3)),
            "wind_kph": max(0, config["wind_kph"] + day_offset)
        })
    return {"location": location, "forecast": forecast, "source": "mock"}
