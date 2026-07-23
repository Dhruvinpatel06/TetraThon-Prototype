import os
from pathlib import Path

# Automatically load local .env file if present in project root
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))
    except Exception:
        pass

# OpenWeatherMap Configuration
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
OPENWEATHER_BASE_URL = os.getenv("OPENWEATHER_BASE_URL", "https://api.openweathermap.org/data/2.5/forecast")
OPENWEATHER_TIMEOUT = int(os.getenv("OPENWEATHER_TIMEOUT", "5"))  # seconds

# Agmarknet / data.gov.in Configuration
AGMARKNET_API_KEY = os.getenv("AGMARKNET_API_KEY", "")
AGMARKNET_BASE_URL = os.getenv("AGMARKNET_BASE_URL", "https://api.data.gov.in/resource/9ef481e1-62ba-4298-a958-7de6d064ec13")
AGMARKNET_TIMEOUT = int(os.getenv("AGMARKNET_TIMEOUT", "5"))  # seconds

# Fallback control flags
WEATHER_FALLBACK_ENABLED = os.getenv("WEATHER_FALLBACK_ENABLED", "true").lower() == "true"
PRICE_FALLBACK_ENABLED = os.getenv("PRICE_FALLBACK_ENABLED", "true").lower() == "true"
