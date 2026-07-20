from pydantic import BaseModel, Field
from typing import Literal


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
    type: Literal["irrigation", "fertiliser", "pest"]
    title: str
    confidence: Literal["High", "Medium", "Low"]
    plain_text: str
    details: dict | None = None


class AdvisoryOutput(BaseModel):
    advisories: list[AdvisoryItem]
    session_id: int  # from FarmerSession DB record


class PostHarvestInput(BaseModel):
    crop_name: str
    quantity_quintals: float = Field(..., gt=0.0)
    storage_condition: Literal["open", "warehouse", "cold_storage"]
    location_name: str


class OptionDetail(BaseModel):
    market: str
    price_per_quintal: float
    transport_cost: float
    net_return: float
    distance_km: float | None = None


class StoreOption(OptionDetail):
    store_days: int
    storage: str
    spoilage_loss: float
    storage_cost: float
    future_price_per_quintal: float


class PostHarvestOutput(BaseModel):
    recommendation: Literal["sell_now", "store", "transport"]
    option_label: str
    expected_return: float
    expected_return_per_quintal: float
    details: dict
    reason: str
    session_id: int