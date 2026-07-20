from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..engine.decision import generate_recommendation

router = APIRouter()


@router.post("/post-harvest", response_model=schemas.PostHarvestOutput)
def create_post_harvest_plan(payload: schemas.PostHarvestInput, db: Session = Depends(get_db)):
    if not payload.location_name.strip() or not payload.crop_name.strip():
        raise HTTPException(
            status_code=400,
            detail="location_name and crop_name cannot be empty."
        )

    # 1. Look up location in DB -> 404 if not found
    location = db.query(models.Location).filter(
        models.Location.name.ilike(payload.location_name.strip())
    ).first()
    if not location:
        raise HTTPException(
            status_code=404,
            detail=f"Location not found: {payload.location_name}"
        )

    # 2. Look up crop in DB -> 404 if not found
    crop = db.query(models.Crop).filter(
        models.Crop.name.ilike(payload.crop_name.strip())
    ).first()
    if not crop:
        raise HTTPException(
            status_code=404,
            detail=f"Crop not found: {payload.crop_name}"
        )

    # 3. Call decision.generate_recommendation(...)
    try:
        recommendation_data = generate_recommendation(
            crop=payload.crop_name,
            quantity=payload.quantity_quintals,
            storage=payload.storage_condition,
            lat=location.latitude,
            lng=location.longitude
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Decision engine failure: {str(e)}"
        )

    # 4. Save a PostHarvestSession record with input details
    session = models.PostHarvestSession(
        location_id=location.id,
        crop_id=crop.id,
        quantity_quintals=payload.quantity_quintals,
        storage_condition=payload.storage_condition,
        recommendation=recommendation_data["recommendation"],
        expected_return=recommendation_data["expected_return"]
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)

    # 5. Return the payload with session_id appended
    return {
        "recommendation": recommendation_data["recommendation"],
        "option_label": recommendation_data["option_label"],
        "expected_return": recommendation_data["expected_return"],
        "expected_return_per_quintal": recommendation_data["expected_return_per_quintal"],
        "details": recommendation_data["details"],
        "reason": recommendation_data["reason"],
        "session_id": session.id
    }
