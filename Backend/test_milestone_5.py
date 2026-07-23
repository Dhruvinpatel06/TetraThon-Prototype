import json
import os
from pathlib import Path

API_JS_PATH = Path("Frontend/src/api.js")
ADVISORY_FORM_PATH = Path("Frontend/src/components/AdvisoryForm.jsx")

def test_milestone_5_frontend_advisory_form():
    """
    Verification test for Chunk 6 - Milestone 5:
    1. Verify postLeafClassify method in Frontend/src/api.js.
    2. Verify photo upload enabled in Frontend/src/components/AdvisoryForm.jsx.
    3. Verify inline classification result display and disclaimer text.
    """
    # 1. Verify api.js
    assert API_JS_PATH.exists(), f"Missing {API_JS_PATH}"
    with open(API_JS_PATH, "r", encoding="utf-8") as f:
        api_code = f.read()

    assert "postLeafClassify" in api_code, "Missing 'postLeafClassify' method in api.js"
    assert "/api/leaf-classify" in api_code, "Missing '/api/leaf-classify' endpoint call in api.js"
    print("[OK] Frontend api.js verified with postLeafClassify method.")

    # 2. Verify AdvisoryForm.jsx
    assert ADVISORY_FORM_PATH.exists(), f"Missing {ADVISORY_FORM_PATH}"
    with open(ADVISORY_FORM_PATH, "r", encoding="utf-8") as f:
        form_code = f.read()

    assert "handleLeafUpload" in form_code, "Missing 'handleLeafUpload' handler in AdvisoryForm.jsx"
    assert "postLeafClassify" in form_code, "Missing 'postLeafClassify' call in AdvisoryForm.jsx"
    assert 'type="file"' in form_code, "Missing file input in AdvisoryForm.jsx"
    assert "AI-assisted analysis" in form_code, "Missing disclaimer label in AdvisoryForm.jsx"
    assert not ('disabled\n' in form_code and 'Coming Soon' in form_code), "Photo upload field is still disabled!"

    print("[OK] AdvisoryForm.jsx photo upload enabled and wired to classification API.")
    print("\nALL MILESTONE 5 VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_milestone_5_frontend_advisory_form()
