import pytest
from App.engine.spoilage import compute_spoilage

def test_spoilage_day_zero():
    res = compute_spoilage("Cotton", "warehouse", 0, 50000.0)
    assert res["value_remaining"] == 50000.0
    assert res["total_loss"] == 0.0
    assert res["loss_percent"] == 0.0

def test_spoilage_decay_intervals():
    # 14 days storage for Cotton in warehouse
    res14 = compute_spoilage("Cotton", "warehouse", 14, 50000.0)
    assert 0 < res14["total_loss"] < 50000.0
    assert res14["value_remaining"] < 50000.0

    # 30 days storage
    res30 = compute_spoilage("Cotton", "warehouse", 30, 50000.0)
    assert res30["total_loss"] > res14["total_loss"]

def test_spoilage_crop_sensitivity():
    # Tomato (highly perishable, modifier 2.0) vs Cotton (modifier 0.5)
    tomato_res = compute_spoilage("Tomato", "open", 10, 10000.0)
    cotton_res = compute_spoilage("Cotton", "open", 10, 10000.0)
    
    assert tomato_res["total_loss"] > cotton_res["total_loss"]

def test_spoilage_max_days_exceeded():
    # Open storage max_days = 60
    res = compute_spoilage("Wheat", "open", 65, 20000.0)
    assert res["value_remaining"] == 0.0
    assert res["total_loss"] == 20000.0
    assert res["loss_percent"] == 100.0

def test_spoilage_edge_cases():
    # Zero initial value
    zero_val = compute_spoilage("Cotton", "warehouse", 10, 0.0)
    assert zero_val["value_remaining"] == 0.0
    assert zero_val["total_loss"] == 0.0

    # Negative days
    neg_days = compute_spoilage("Cotton", "warehouse", -5, 10000.0)
    assert neg_days["value_remaining"] == 10000.0
