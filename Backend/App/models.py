from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from .database import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    state = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)


class Crop(Base):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    typical_duration_days = Column(Integer, nullable=False)
    category = Column(String, nullable=False)


class FarmerSession(Base):
    __tablename__ = "farmer_sessions"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=True)
    sowing_date = Column(DateTime, nullable=True)
    weather_observation = Column(String, nullable=True)
    photo_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PostHarvestSession(Base):
    __tablename__ = "post_harvest_sessions"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=True)
    quantity_quintals = Column(Float, nullable=False)
    storage_condition = Column(String, nullable=False)
    recommendation = Column(String, nullable=False)  # "sell_now" | "store" | "transport"
    expected_return = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())