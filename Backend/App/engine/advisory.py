import json
import datetime
from pathlib import Path
from App.adapters.weather import get_forecast

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
RULES_DIR = BASE_DIR / "data"

# Water depth mapping per stage (in cm)
STAGE_WATER_DEPTH = {
    # Cotton stages
    "germination": 5.0,
    "vegetative": 7.5,
    "flowering_boll": 10.0,
    "maturity": 0.0,
    # Wheat stages
    "tillering": 5.0,
    "flowering_grain_fill": 7.5,
    # Groundnut stages
    "flowering_pegging": 7.5,
    "pod_maturity": 5.0,
    # Tomato stages
    "flowering_fruiting": 7.5,
}


def load_rules(filename: str) -> dict:
    filepath = RULES_DIR / filename
    with open(filepath, "r") as f:
        return json.load(f)


def get_crop_rules(rules_dict: dict, crop_name: str) -> list | None:
    for key, value in rules_dict.items():
        if key.strip().lower() == crop_name.strip().lower():
            return value
    return None


def find_rule_for_day(rules: list, days: int) -> tuple[dict | None, bool]:
    """
    Returns (matched_rule, is_generic_fallback).
    If days is within range of a rule, returns (rule, False).
    If days exceeds maximum range, returns (last_rule, True).
    Otherwise returns (None, True).
    """
    for r in rules:
        start, end = r["days_range"]
        if start <= days <= end:
            return r, False
            
    # Generic fallback to the last stage if days exceed normal duration
    if rules and days > rules[-1]["days_range"][1]:
        return rules[-1], True
        
    return None, True


def generate_advisories(
    location_name: str,
    crop_name: str,
    sowing_date_str: str,
    weather_observation: str | None
) -> list[dict]:
    """
    Generates 3 ranked advisories (irrigation, fertiliser, pest) with confidence
    and plain-language advisory messages based on farmer inputs, rules, and weather forecast.
    """
    # 1. Parse sowing date
    try:
        sowing_date = datetime.date.fromisoformat(sowing_date_str)
    except ValueError:
        raise ValueError("Invalid sowing date format. Use YYYY-MM-DD.")

    # Calculate days since sowing
    days_since_sowing = (datetime.date.today() - sowing_date).days

    # Load rules
    try:
        irrigation_data = load_rules("irrigation_rules.json")
        fertiliser_data = load_rules("fertiliser_rules.json")
        pest_data = load_rules("pest_rules.json")
    except Exception as e:
        raise RuntimeError(f"Failed to load rule JSON files: {str(e)}")

    irrigation_rules = get_crop_rules(irrigation_data, crop_name)
    fertiliser_rules = get_crop_rules(fertiliser_data, crop_name)
    pest_rules = get_crop_rules(pest_data, crop_name)

    if not irrigation_rules or not fertiliser_rules or not pest_rules:
        raise ValueError(f"Rules not found for crop: {crop_name}")

    # Determine typical duration based on the rules (max days_range end)
    typical_duration_days = irrigation_rules[-1]["days_range"][1]

    # Handle extreme edge cases (Future / Very Old)
    if days_since_sowing < 0:
        return [
            {
                "type": "irrigation",
                "title": "Irrigation Advisory",
                "confidence": "Low",
                "plain_text": "Sowing date is in the future. Please select a valid sowing date to receive irrigation advisories.",
                "details": {"error": "Future sowing date"}
            },
            {
                "type": "fertiliser",
                "title": "Fertiliser Advisory",
                "confidence": "Low",
                "plain_text": "Sowing date is in the future. Please select a valid sowing date to receive fertiliser advisories.",
                "details": {"error": "Future sowing date"}
            },
            {
                "type": "pest",
                "title": "Pest Advisory",
                "confidence": "Low",
                "plain_text": "Sowing date is in the future. Please select a valid sowing date to receive pest advisories.",
                "details": {"error": "Future sowing date"}
            }
        ]

    if days_since_sowing > 2 * typical_duration_days:
        return [
            {
                "type": "irrigation",
                "title": "Irrigation Advisory",
                "confidence": "Low",
                "plain_text": "Crop likely harvested. Verify sowing date to get active irrigation advisories.",
                "details": {"error": "Crop likely harvested"}
            },
            {
                "type": "fertiliser",
                "title": "Fertiliser Advisory",
                "confidence": "Low",
                "plain_text": "Crop likely harvested. Verify sowing date to get active fertiliser advisories.",
                "details": {"error": "Crop likely harvested"}
            },
            {
                "type": "pest",
                "title": "Pest Advisory",
                "confidence": "Low",
                "plain_text": "Crop likely harvested. Verify sowing date to get active pest advisories.",
                "details": {"error": "Crop likely harvested"}
            }
        ]

    # Find rules for current day
    ir_rule, ir_generic = find_rule_for_day(irrigation_rules, days_since_sowing)
    fe_rule, fe_generic = find_rule_for_day(fertiliser_rules, days_since_sowing)
    pe_rule, pe_generic = find_rule_for_day(pest_rules, days_since_sowing)

    if not ir_rule or not fe_rule or not pe_rule:
        raise ValueError("Could not determine rules for the given sowing date.")

    # Get weather forecast
    forecast_data = None
    weather_error = False
    try:
        forecast_data = get_forecast(location_name)
    except ValueError:
        weather_error = True

    # 2. Determine active weather conditions
    active_conditions = set()

    # Map user's weather observation
    if weather_observation == "hot_and_dry":
        active_conditions.update(["hot_dry", "dry_soil"])
    elif weather_observation == "humid_cloudy":
        active_conditions.update(["humid", "high_humidity", "cool_humid"])
    elif weather_observation in ("light_rain", "heavy_rain"):
        active_conditions.update(["humid", "high_humidity", "rain_expected"])
        if weather_observation == "heavy_rain":
            active_conditions.add("waterlogged")

    # Map weather forecast conditions
    if forecast_data:
        # rain expected if any day in forecast has rain_chance >= 50
        if any(day["rain_chance"] >= 50 for day in forecast_data["forecast"]):
            active_conditions.add("rain_expected")
        # high humidity if any day has humidity >= 70
        if any(day["humidity"] >= 70 for day in forecast_data["forecast"]):
            active_conditions.add("high_humidity")
            active_conditions.add("humid")
        # cool/humid if temp low <= 20 and humidity >= 70
        if any(day["temp_low"] <= 20 and day["humidity"] >= 70 for day in forecast_data["forecast"]):
            active_conditions.add("cool_humid")
        # hot/dry if temp high >= 40 and humidity <= 50
        if any(day["temp_high"] >= 40 and day["humidity"] <= 50 for day in forecast_data["forecast"]):
            active_conditions.add("hot_dry")
            active_conditions.add("dry_soil")
        # warm night if temp low >= 25
        if any(day["temp_low"] >= 25 for day in forecast_data["forecast"]):
            active_conditions.add("warm_night")

    # 3. Score and format IRRIGATION advisory
    # Confidence scoring
    if weather_error:
        ir_confidence = "Low"
    elif not weather_observation:
        ir_confidence = "Medium"
    else:
        ir_confidence = "High"

    ir_stage_display = ir_rule["stage"].replace("_", " ").title()
    water_cm = STAGE_WATER_DEPTH.get(ir_rule["stage"], 5.0)
    freq = ir_rule["interval_days"]

    rain_advice = ""
    if forecast_data:
        rainy_days_count = sum(1 for day in forecast_data["forecast"] if day["rain_chance"] >= 50)
        skip_window = ir_rule.get("skip_window_days", 0)
        skip_if_rain = ir_rule.get("skip_if_rain_expected", False)
        
        # Check if rain is expected in the skip window
        rain_in_skip_window = False
        if skip_if_rain and skip_window > 0:
            for day in forecast_data["forecast"][:skip_window]:
                if day["rain_chance"] >= 50:
                    rain_in_skip_window = True
                    break

        if rain_in_skip_window:
            rain_advice = f"Rain expected within the next {skip_window} days — skip or delay irrigation."
        elif rainy_days_count > 0:
            rain_advice = f"Rain expected on {rainy_days_count} of the next 7 days — reduce watering accordingly."
        else:
            rain_advice = "No significant rain expected — maintain regular schedule."
    else:
        rain_advice = "Monitor soil moisture locally."

    ir_plain_text = f"Your {crop_name} is in the {ir_stage_display} stage. Apply {water_cm:.1f}cm of water every {freq} day(s). {rain_advice}"
    
    ir_details = {
        "stage": ir_stage_display,
        "day_range": ir_rule["days_range"],
        "interval_days": freq,
        "water_cm": water_cm,
        "skip_if_rain_expected": ir_rule.get("skip_if_rain_expected", False),
        "skip_window_days": ir_rule.get("skip_window_days", 0),
        "is_generic_fallback": ir_generic
    }

    # 4. Score and format FERTILISER advisory
    # Confidence scoring
    if fe_generic:
        fe_confidence = "Medium"
    else:
        fe_confidence = "High"

    fe_stage_display = fe_rule["stage"].replace("_", " ").title()
    n_kg = fe_rule["npk_kg_per_acre"]["N"]
    p_kg = fe_rule["npk_kg_per_acre"]["P"]
    k_kg = fe_rule["npk_kg_per_acre"]["K"]
    note = fe_rule.get("note", "")

    fe_plain_text = f"Your {crop_name} is in the {fe_stage_display} stage. Apply {n_kg}kg Nitrogen, {p_kg}kg Phosphorus, {k_kg}kg Potassium per acre."
    if note:
        fe_plain_text += f" Note: {note}."

    fe_details = {
        "stage": fe_stage_display,
        "day_range": fe_rule["days_range"],
        "npk_kg_per_acre": fe_rule["npk_kg_per_acre"],
        "note": note,
        "is_generic_fallback": fe_generic
    }

    # 5. Score and format PEST advisory
    # Confidence scoring
    if pe_generic or weather_error or not weather_observation:
        pe_confidence = "Medium"
    else:
        pe_confidence = "High"

    pe_stage_display = pe_rule["stage"].replace("_", " ").title()
    pest_name = pe_rule["pest_or_disease"]
    default_risk = pe_rule["risk_level"]

    # Factoring weather conditions to elevate risk level
    has_elevating_factor = False
    for condition in pe_rule.get("raises_risk_if", []):
        if condition in active_conditions:
            has_elevating_factor = True
            break

    if has_elevating_factor:
        if default_risk == "Low":
            final_risk = "Medium"
        elif default_risk == "Medium":
            final_risk = "High"
        else:
            final_risk = "High"
        observation_advice = "Weather conditions raise the risk of this pest/disease. Inspect crop closely."
    else:
        final_risk = default_risk
        observation_advice = "Monitor crop regularly for signs of infestation."

    pe_plain_text = f"Your {crop_name} is in the {pe_stage_display} stage. Watch for {pest_name} (Risk: {final_risk}). {observation_advice}"

    pe_details = {
        "stage": pe_stage_display,
        "day_range": pe_rule["days_range"],
        "pest_or_disease": pest_name,
        "default_risk": default_risk,
        "calculated_risk": final_risk,
        "raises_risk_if": pe_rule.get("raises_risk_if", []),
        "is_generic_fallback": pe_generic
    }

    # 6. Rank 3 advisories in fixed order (irrigation, fertiliser, pest)
    return [
        {
            "type": "irrigation",
            "title": "Irrigation Advisory",
            "confidence": ir_confidence,
            "plain_text": ir_plain_text,
            "details": ir_details
        },
        {
            "type": "fertiliser",
            "title": "Fertiliser Advisory",
            "confidence": fe_confidence,
            "plain_text": fe_plain_text,
            "details": fe_details
        },
        {
            "type": "pest",
            "title": "Pest Advisory",
            "confidence": pe_confidence,
            "plain_text": pe_plain_text,
            "details": pe_details
        }
    ]
