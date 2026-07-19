from pydantic import BaseModel


class LocationOut(BaseModel):
    id: int
    name: str
    state: str
    latitude: float
    longitude: float

    class Config:
        from_attributes = True


class CropOut(BaseModel):
    id: int
    name: str
    typical_duration_days: int
    category: str

    class Config:
        from_attributes = True


class AdvisoryInput(BaseModel):
    location_name: str
    crop_name: str
    sowing_date: str  # ISO format YYYY-MM-DD
    weather_observation: str | None = None  # "hot_and_dry", "humid_cloudy", "light_rain", "heavy_rain", null


class AdvisoryItem(BaseModel):
    type: str
    title: str
    confidence: str  # "High" | "Medium" | "Low"
    plain_text: str
    details: dict | None = None


class AdvisoryOutput(BaseModel):
    advisories: list[AdvisoryItem]
    session_id: int  # from FarmerSession DB record