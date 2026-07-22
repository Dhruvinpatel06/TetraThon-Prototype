import sys
import os

# Ensure UTF-8 output encoding for Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from pathlib import Path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from unittest.mock import patch, MagicMock
import httpx
from App.adapters.market_prices import load_prices, get_latest_price, get_future_price, get_price_adapter_status
from App.engine.decision import generate_recommendation


def test_price_fallback_no_api_key():
    print("Testing Milestone 6: Fallback Scenario 1 — No AGMARKNET API Key Set...")
    with patch("App.adapters.market_prices.AGMARKNET_API_KEY", ""):
        # Clear live cache for test isolation
        with patch.dict("App.adapters.market_prices._live_prices_cache", {}, clear=True):
            prices = load_prices("Cotton", "Ahmedabad APMC")
            assert len(prices) > 0, "Expected CSV fallback data"
            assert get_price_adapter_status("Cotton", "Ahmedabad APMC") == "mock"
            print("  [OK] Successfully fell back to mandi_prices.csv when AGMARKNET_API_KEY is empty.")


def test_price_fallback_invalid_api_key_401():
    print("\nTesting Milestone 6: Fallback Scenario 2 — Invalid API Key (HTTP 401)...")
    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError("401 Unauthorized", request=MagicMock(), response=mock_resp)

    with patch("App.adapters.market_prices.AGMARKNET_API_KEY", "invalid_key"):
        with patch.dict("App.adapters.market_prices._live_prices_cache", {}, clear=True):
            with patch("httpx.Client.get", return_value=mock_resp):
                prices = load_prices("Wheat", "Vadodara APMC")
                assert len(prices) > 0, "Expected CSV fallback data"
                assert get_price_adapter_status("Wheat", "Vadodara APMC") == "mock"
                print("  [OK] Successfully fell back to mandi_prices.csv on HTTP 401 Unauthorized.")


def test_price_fallback_server_error_500():
    print("\nTesting Milestone 6: Fallback Scenario 3 — Server Error (HTTP 500)...")
    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError("500 Internal Server Error", request=MagicMock(), response=mock_resp)

    with patch("App.adapters.market_prices.AGMARKNET_API_KEY", "some_key"):
        with patch.dict("App.adapters.market_prices._live_prices_cache", {}, clear=True):
            with patch("httpx.Client.get", return_value=mock_resp):
                prices = load_prices("Groundnut", "Surat APMC")
                assert len(prices) > 0, "Expected CSV fallback data"
                assert get_price_adapter_status("Groundnut", "Surat APMC") == "mock"
                print("  [OK] Successfully fell back to mandi_prices.csv on HTTP 500 Server Error.")


def test_price_fallback_timeout():
    print("\nTesting Milestone 6: Fallback Scenario 4 — Network Timeout (>5s)...")
    with patch("App.adapters.market_prices.AGMARKNET_API_KEY", "some_key"):
        with patch.dict("App.adapters.market_prices._live_prices_cache", {}, clear=True):
            with patch("httpx.Client.get", side_effect=httpx.TimeoutException("Connection timed out")):
                prices = load_prices("Tomato", "Rajkot APMC")
                assert len(prices) > 0, "Expected CSV fallback data"
                assert get_price_adapter_status("Tomato", "Rajkot APMC") == "mock"
                print("  [OK] Successfully fell back to mandi_prices.csv on TimeoutException.")


def test_price_fallback_decision_engine_regression():
    print("\nTesting Milestone 6: Decision Engine Regression Test Under Fallback Mode...")
    with patch("App.adapters.market_prices.AGMARKNET_API_KEY", ""):
        with patch.dict("App.adapters.market_prices._live_prices_cache", {}, clear=True):
            rec = generate_recommendation("Cotton", 50.0, "warehouse", 23.0225, 72.5714)
            assert "recommendation" in rec
            assert rec["recommendation"] in ["sell_now", "store", "transport"]
            assert rec["expected_return"] > 0
            assert "details" in rec
            print(f"  [OK] Decision Engine executed cleanly under fallback: {rec['option_label']} (INR {rec['expected_return']}).")


if __name__ == "__main__":
    print("=== STARTING MILESTONE 6 VERIFICATION ===")
    test_price_fallback_no_api_key()
    test_price_fallback_invalid_api_key_401()
    test_price_fallback_server_error_500()
    test_price_fallback_timeout()
    test_price_fallback_decision_engine_regression()
    print("\n=== MILESTONE 6 VERIFICATION COMPLETED SUCCESSFULLY! ===")
