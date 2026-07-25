import pytest
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from App.database import Base
from App.models import Location, Crop

# In-memory SQLite DB for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        # Seed test data
        loc = Location(name="Anand", state="Gujarat", latitude=22.5645, longitude=72.9289)
        crop = Crop(name="Cotton", typical_duration_days=180, category="cash_crop")
        db.add_all([loc, crop])
        db.commit()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_advisory_input():
    return {
        "location_name": "Anand",
        "crop_name": "Cotton",
        "sowing_date_str": (datetime.date.today() - datetime.timedelta(days=45)).isoformat(),
        "weather_observation": "hot_and_dry"
    }
