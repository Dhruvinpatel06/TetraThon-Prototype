import os
from pathlib import Path
from dotenv import load_dotenv

# Automatically load local .env file if present in project root
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

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
