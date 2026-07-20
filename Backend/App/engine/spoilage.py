def compute_spoilage(crop: str, storage: str, days: int, initial_value: float) -> dict:
    """
    Computes spoilage loss based on crop, storage condition, days, and initial value.
    Returns a dict with value_remaining, loss_percent, and total_loss.
    """
    # Normalize inputs
    crop_norm = crop.strip().capitalize() if crop else ""
    storage_norm = storage.strip().lower() if storage else ""
    days = max(0, days)
    initial_value = max(0.0, initial_value)
    
    # Storage configuration
    storage_config = {
        "open": {"base_rate": 0.015, "max_days": 60},
        "warehouse": {"base_rate": 0.006, "max_days": 150},
        "cold_storage": {"base_rate": 0.0015, "max_days": 600}
    }
    
    # Crop modifier
    crop_modifiers = {
        "Tomato": 2.0,
        "Groundnut": 0.7,
        "Cotton": 0.5,
        "Wheat": 0.8
    }
    
    cfg = storage_config.get(storage_norm, {"base_rate": 0.015, "max_days": 60})
    modifier = crop_modifiers.get(crop_norm, 1.0)
    
    # Total loss if days stored exceeds max days
    if days >= cfg["max_days"]:
        value_remaining = 0.0
    else:
        effective_daily_rate = cfg["base_rate"] * modifier
        effective_daily_rate = min(1.0, max(0.0, effective_daily_rate))
        value_remaining = initial_value * ((1.0 - effective_daily_rate) ** days)
        value_remaining = max(0.0, min(initial_value, value_remaining))
        
    total_loss = initial_value - value_remaining
    loss_percent = (total_loss / initial_value * 100.0) if initial_value > 0 else 0.0
    
    return {
        "value_remaining": round(value_remaining, 2),
        "loss_percent": round(loss_percent, 2),
        "total_loss": round(total_loss, 2)
    }
