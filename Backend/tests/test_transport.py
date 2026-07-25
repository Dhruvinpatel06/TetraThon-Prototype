import pytest
from App.engine.transport import haversine, transport_cost, MARKETS

def test_haversine_same_point():
    # Distance to same point should be 0.0
    dist = haversine(23.0225, 72.5714, 23.0225, 72.5714)
    assert round(dist, 4) == 0.0

def test_haversine_known_coordinates():
    # Ahmedabad APMC (23.0225, 72.5714) to Anand APMC (22.5645, 72.9289) ~60-70 km
    dist = haversine(23.0225, 72.5714, 22.5645, 72.9289)
    assert 50.0 < dist < 80.0

def test_transport_cost_minimum_enforcement():
    # Very small quantity (0.1 quintal) over short distance should enforce ₹500 min charge
    costs = transport_cost(23.0225, 72.5714, 0.1)
    assert len(costs) == 5
    for item in costs:
        assert item["transport_cost"] >= 500.0

def test_transport_cost_calculation():
    # Large quantity (50 quintals) over distance
    costs = transport_cost(22.5645, 72.9289, 50.0)
    ahmedabad = next(c for c in costs if c["market"] == "Ahmedabad APMC")
    expected = max(500.0, haversine(22.5645, 72.9289, 23.0225, 72.5714) * 5.0 * 50.0)
    assert abs(ahmedabad["transport_cost"] - round(expected, 2)) < 1.0

def test_transport_cost_zero_quantity():
    # 0 quantity should return 0.0 transport cost for all markets
    costs = transport_cost(23.0225, 72.5714, 0.0)
    for c in costs:
        assert c["transport_cost"] == 0.0
