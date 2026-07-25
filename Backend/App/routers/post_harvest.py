from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..engine.decision import generate_recommendation
from ..engine.spoilage import compute_spoilage
from ..adapters.market_prices import load_prices, get_latest_price
from ..limiter import limiter

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


@router.get("/price-history")
@limiter.limit("30/minute")
def get_price_history(request: Request, crop: str = "Cotton", location: str = "Ahmedabad"):
    target_crop = crop.strip().title() if crop else "Cotton"
    market_names = [
        "Ahmedabad APMC", "Surat APMC", "Vadodara APMC", "Rajkot APMC", "Anand APMC"
    ]
    
    market_histories = {m: load_prices(target_crop, m) for m in market_names}
    non_empty_lengths = [len(h) for h in market_histories.values() if h]
    if not non_empty_lengths:
        return {"crop": target_crop, "location": location, "history": []}
        
    sample_len = min(non_empty_lengths)
    if sample_len == 0:
        return {"crop": target_crop, "location": location, "history": []}
    
    step = max(1, sample_len // 12)
    indices = list(range(0, sample_len, step))[-12:]
    
    formatted_trend = []
    for idx in indices:
        # Find first non-empty market to extract date label
        date_label = f"Pt {idx}"
        for m in market_names:
            history = market_histories.get(m, [])
            if history and idx < len(history):
                date_label = history[idx].get("date", f"Pt {idx}")
                break
                
        point = {"date": date_label}
        for m in market_names:
            history = market_histories.get(m, [])
            if history and idx < len(history):
                point[m] = history[idx].get("price", 0.0)
        formatted_trend.append(point)
        
    return {"crop": target_crop, "location": location, "history": formatted_trend}


@router.get("/spoilage-curve")
@limiter.limit("30/minute")
def get_spoilage_curve(request: Request, crop: str = "Cotton", quantity: float = 10.0):
    target_crop = crop.strip().title() if crop else "Cotton"
    qty = max(0.1, float(quantity))
    
    price_per_q = get_latest_price(target_crop, "Ahmedabad APMC")
    if price_per_q <= 0:
        base_prices = {"Cotton": 6200.0, "Wheat": 2400.0, "Groundnut": 5800.0, "Tomato": 1800.0}
        price_per_q = base_prices.get(target_crop, 5000.0)
        
    initial_val = price_per_q * qty
    
    curve = []
    for day in range(31):
        open_res = compute_spoilage(target_crop, "open", day, initial_val)
        wh_res = compute_spoilage(target_crop, "warehouse", day, initial_val)
        cs_res = compute_spoilage(target_crop, "cold_storage", day, initial_val)
        
        curve.append({
            "day": f"Day {day}",
            "open": int(open_res["value_remaining"]),
            "warehouse": int(wh_res["value_remaining"]),
            "cold_storage": int(cs_res["value_remaining"])
        })
        
    return {"crop": target_crop, "quantity": qty, "curve": curve}
