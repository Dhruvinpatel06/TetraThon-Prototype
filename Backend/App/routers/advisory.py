from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from ..database import get_db
from .. import models, schemas
from ..engine.advisory import generate_advisories

router = APIRouter()


@router.post("/advisory", response_model=schemas.AdvisoryOutput)
@router.post("/api/advisory", response_model=schemas.AdvisoryOutput)
def create_advisory(payload: schemas.AdvisoryInput, db: Session = Depends(get_db)):
    # 1. Look up location and crop in DB -> 404 if not found
    location = db.query(models.Location).filter(
        models.Location.name == payload.location_name
    ).first()
    if not location:
        raise HTTPException(
            status_code=404,
            detail=f"Location not found: {payload.location_name}"
        )

    crop = db.query(models.Crop).filter(
        models.Crop.name == payload.crop_name
    ).first()
    if not crop:
        raise HTTPException(
            status_code=404,
            detail=f"Crop not found: {payload.crop_name}"
        )

    # Validate sowing date format
    try:
        sowing_date_dt = datetime.strptime(payload.sowing_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid sowing date format. Must be YYYY-MM-DD."
        )

    # 2. Call engine.generate_advisories(...)
    try:
        advisories_data = generate_advisories(
            location_name=payload.location_name,
            crop_name=payload.crop_name,
            sowing_date_str=payload.sowing_date,
            weather_observation=payload.weather_observation
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Advisory generation failed: {str(e)}"
        )

    # 3. Save a FarmerSession record with input details
    session = models.FarmerSession(
        location_id=location.id,
        crop_id=crop.id,
        sowing_date=sowing_date_dt,
        weather_observation=payload.weather_observation,
        photo_path=None  # Coming soon
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # 4. Return { advisories: [...], session_id: N }
    return {
        "advisories": advisories_data,
        "session_id": session.id
    }
