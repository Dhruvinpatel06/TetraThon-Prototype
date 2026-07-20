from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models
from ..engine.advisory import load_rules, get_crop_rules

router = APIRouter()


@router.get("/rules")
def get_rules(
    crop_id: int | None = None,
    crop_name: str | None = None,
    db: Session = Depends(get_db)
):
    """
    Returns all 3 rule tables (irrigation, fertiliser, pest) for the specified crop,
    merged into one response. Supports lookup by crop_id or crop_name.
    """
    if crop_id is None and (crop_name is None or not crop_name.strip()):
        raise HTTPException(
            status_code=400,
            detail="Provide either crop_id or crop_name query parameter."
        )

    crop = None
    if crop_id is not None:
        crop = db.query(models.Crop).filter(models.Crop.id == crop_id).first()
    else:
        crop = db.query(models.Crop).filter(
            models.Crop.name.ilike(crop_name.strip())
        ).first()

    if not crop:
        raise HTTPException(
            status_code=404,
            detail=f"Crop not found for crop_id={crop_id} or crop_name='{crop_name}'"
        )

    try:
        irrigation_data = load_rules("irrigation_rules.json")
        fertiliser_data = load_rules("fertiliser_rules.json")
        pest_data = load_rules("pest_rules.json")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load rule files: {str(e)}"
        )

    irrigation_rules = get_crop_rules(irrigation_data, crop.name)
    fertiliser_rules = get_crop_rules(fertiliser_data, crop.name)
    pest_rules = get_crop_rules(pest_data, crop.name)

    if irrigation_rules is None or fertiliser_rules is None or pest_rules is None:
        raise HTTPException(
            status_code=404,
            detail=f"Rules not found for crop '{crop.name}'"
        )

    return {
        "crop_name": crop.name,
        "irrigation": irrigation_rules,
        "fertiliser": fertiliser_rules,
        "pest": pest_rules
    }
