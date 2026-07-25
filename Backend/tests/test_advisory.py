import pytest
import datetime
from App.engine.advisory import (
    load_rules,
    get_crop_rules,
    find_rule_for_day,
    generate_advisories
)

def test_load_rules_and_caching():
    irr_rules = load_rules("irrigation_rules.json")
    fert_rules = load_rules("fertiliser_rules.json")
    pest_rules = load_rules("pest_rules.json")
    
    assert "Cotton" in irr_rules
    assert "Wheat" in fert_rules
    assert "Groundnut" in pest_rules

def test_get_crop_rules():
    irr_rules = load_rules("irrigation_rules.json")
    cotton_rules = get_crop_rules(irr_rules, "cotton")
    assert cotton_rules is not None
    assert len(cotton_rules) > 0
    
    unknown = get_crop_rules(irr_rules, "NonExistentCrop")
    assert unknown is None

def test_find_rule_for_day():
    rules = [
        {"stage": "germination", "days_range": [0, 20]},
        {"stage": "vegetative", "days_range": [21, 70]}
    ]
    rule, fallback = find_rule_for_day(rules, 10)
    assert rule["stage"] == "germination"
    assert fallback is False

    # Exceeding range fallback
    rule_fall, fallback_flag = find_rule_for_day(rules, 100)
    assert rule_fall["stage"] == "vegetative"
    assert fallback_flag is True

def test_generate_advisories_all_crops(sample_advisory_input):
    crops = ["Cotton", "Wheat", "Groundnut", "Tomato"]
    for crop in crops:
        sowing_date = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
        advisories = generate_advisories("Anand", crop, sowing_date, "hot_dry")
        assert len(advisories) == 3
        types = {a["type"] for a in advisories}
        assert types == {"irrigation", "fertiliser", "pest"}
        for a in advisories:
            assert "plain_text" in a
            assert "confidence" in a

def test_generate_advisories_future_sowing_date():
    future_date = (datetime.date.today() + datetime.timedelta(days=10)).isoformat()
    advisories = generate_advisories("Anand", "Cotton", future_date, None)
    assert len(advisories) == 3
    for a in advisories:
        assert "future" in a["plain_text"].lower()

def test_generate_advisories_invalid_inputs():
    with pytest.raises(ValueError, match="Invalid sowing date format"):
        generate_advisories("Anand", "Cotton", "invalid-date", None)
        
    with pytest.raises(ValueError, match="Rules not found"):
        generate_advisories("Anand", "UnknownCrop", "2026-05-15", None)
