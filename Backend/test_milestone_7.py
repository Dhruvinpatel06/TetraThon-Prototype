import json
import os
from pathlib import Path

LEAF_RESULT_PATH = Path("Frontend/src/components/LeafResult.jsx")
ADVISORY_RESULT_PATH = Path("Frontend/src/components/AdvisoryResult.jsx")
DASHBOARD_PATH = Path("Frontend/src/components/Dashboard.jsx")

def test_milestone_7_leaf_result_display():
    """
    Verification test for Chunk 6 - Milestone 7:
    1. Verify Frontend/src/components/LeafResult.jsx component created and structured correctly.
    2. Verify LeafResult rendering in AdvisoryResult.jsx.
    3. Verify LeafResult rendering in Dashboard.jsx.
    4. Verify KVK consultation disclaimer text present in LeafResult.jsx.
    """
    # 1. Verify LeafResult.jsx
    assert LEAF_RESULT_PATH.exists(), f"Missing {LEAF_RESULT_PATH}"
    with open(LEAF_RESULT_PATH, "r", encoding="utf-8") as f:
        code = f.read()

    assert "Leaf Image Analysis" in code, "Missing header title in LeafResult.jsx"
    assert "is_healthy" in code, "Missing healthy/diseased status logic in LeafResult.jsx"
    assert "confidence" in code, "Missing confidence badge in LeafResult.jsx"
    assert "certified diagnosis" in code, "Missing disclaimer text in LeafResult.jsx"
    print("[OK] LeafResult.jsx component created and verified.")

    # 2. Verify AdvisoryResult.jsx
    assert ADVISORY_RESULT_PATH.exists(), f"Missing {ADVISORY_RESULT_PATH}"
    with open(ADVISORY_RESULT_PATH, "r", encoding="utf-8") as f:
        adv_code = f.read()

    assert "LeafResult" in adv_code, "LeafResult component not imported/used in AdvisoryResult.jsx"
    print("[OK] LeafResult integrated into AdvisoryResult.jsx.")

    # 3. Verify Dashboard.jsx
    assert DASHBOARD_PATH.exists(), f"Missing {DASHBOARD_PATH}"
    with open(DASHBOARD_PATH, "r", encoding="utf-8") as f:
        dash_code = f.read()

    assert "LeafResult" in dash_code, "LeafResult component not imported/used in Dashboard.jsx"
    print("[OK] LeafResult integrated into Dashboard.jsx.")

    print("\nALL MILESTONE 7 VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_milestone_7_leaf_result_display()
