import pytest
from App.engine.decision import find_closest_market, generate_recommendation

def test_find_closest_market():
    # Ahmedabad coordinates
    closest = find_closest_market(23.0225, 72.5714)
    assert closest == "Ahmedabad APMC"

    # Anand coordinates
    closest_anand = find_closest_market(22.5645, 72.9289)
    assert closest_anand == "Anand APMC"

def test_generate_recommendation_structure():
    res = generate_recommendation("Cotton", 10.0, "warehouse", 23.0225, 72.5714)
    assert res["recommendation"] in ["sell_now", "store", "transport"]
    assert "option_label" in res
    assert "expected_return" in res
    assert "expected_return_per_quintal" in res
    assert "details" in res
    assert "reason" in res
    assert "sell_now" in res["details"]
    assert "store" in res["details"]
    assert "transport" in res["details"]

def test_generate_recommendation_zero_quantity():
    res = generate_recommendation("Cotton", 0.0, "warehouse", 23.0225, 72.5714)
    assert res["expected_return_per_quintal"] == 0.0

def test_generate_recommendation_case_insensitivity():
    res = generate_recommendation("cotton", 15.0, "WAREHOUSE", 22.5645, 72.9289)
    assert res["details"]["store"]["storage"] == "WAREHOUSE"
    assert res["recommendation"] in ["sell_now", "store", "transport"]
