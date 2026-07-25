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


@router.get("/price-history")
def get_price_history(crop: str = "Cotton", location: str = "Ahmedabad"):
    from ..adapters.market_prices import load_prices
    target_crop = crop.strip().capitalize() if crop else "Cotton"
    market_names = [
        "Ahmedabad APMC", "Surat APMC", "Vadodara APMC", "Rajkot APMC", "Anand APMC"
    ]
    
    market_histories = {m: load_prices(target_crop, m) for m in market_names}
    sample_len = min(len(h) for h in market_histories.values() if h) if any(market_histories.values()) else 0
    if sample_len == 0:
        return {"crop": target_crop, "history": []}
    
    step = max(1, sample_len // 12)
    indices = list(range(0, sample_len, step))[-12:]
    
    formatted_trend = []
    for idx in indices:
        date_label = market_histories["Ahmedabad APMC"][idx]["date"] if market_histories["Ahmedabad APMC"] else f"Pt {idx}"
        point = {"date": date_label}
        for m in market_names:
            if market_histories[m] and idx < len(market_histories[m]):
                point[m] = market_histories[m][idx]["price"]
        formatted_trend.append(point)
        
    return {"crop": target_crop, "location": location, "history": formatted_trend}


@router.get("/spoilage-curve")
def get_spoilage_curve(crop: str = "Cotton", quantity: float = 10.0):
    from ..engine.spoilage import compute_spoilage
    from ..adapters.market_prices import get_latest_price
    
    target_crop = crop.strip().capitalize() if crop else "Cotton"
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
