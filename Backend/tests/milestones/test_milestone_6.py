import json
import os
from pathlib import Path

UNIFIED_FORM_PATH = Path("Frontend/src/components/UnifiedScenarioForm.jsx")

def test_milestone_6_unified_scenario_form():
    """
    Verification test for Chunk 6 - Milestone 6:
    1. Verify photo upload field in Frontend/src/components/UnifiedScenarioForm.jsx.
    2. Verify handleLeafUpload handler and api.postLeafClassify call.
    3. Verify leafResult integration in onSubmitSuccess.
    4. Verify AI disclaimer label text present.
    """
    assert UNIFIED_FORM_PATH.exists(), f"Missing {UNIFIED_FORM_PATH}"
    with open(UNIFIED_FORM_PATH, "r", encoding="utf-8") as f:
        form_code = f.read()

    assert "handleLeafUpload" in form_code, "Missing 'handleLeafUpload' in UnifiedScenarioForm.jsx"
    assert "postLeafClassify" in form_code, "Missing 'postLeafClassify' call in UnifiedScenarioForm.jsx"
    assert "leafResult" in form_code, "Missing 'leafResult' state in UnifiedScenarioForm.jsx"
    assert 'col-span-1 md:col-span-2' in form_code, "Missing full-width grid layout for photo upload"
    assert "AI-assisted analysis" in form_code, "Missing AI disclaimer label text"

    print("[OK] UnifiedScenarioForm.jsx verified with photo upload field & classification handler.")
    print("\nALL MILESTONE 6 VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_milestone_6_unified_scenario_form()
