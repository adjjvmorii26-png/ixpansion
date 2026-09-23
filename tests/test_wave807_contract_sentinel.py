"""Wave 807 contract sentinel tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))

import wave807_contract_sentinel as w807


def test_evaluate_reports_gaps():
    snap = {
        "total": 3,
        "valid": 2,
        "stateful": 0,
        "organs": [
            {
                "name": "good",
                "valid": True,
                "contract": {
                    "handler": True,
                    "coherence_vitals": True,
                    "resonates_with": True,
                },
            },
            {
                "name": "gap",
                "valid": True,
                "contract": {
                    "handler": True,
                    "coherence_vitals": False,
                    "resonates_with": False,
                },
            },
            {"name": "broken", "valid": False},
        ],
    }
    verdict = w807.evaluate(snap)
    assert verdict["ok"] is False
    assert verdict["gap_count"] == 1
    assert verdict["gaps"][0]["name"] == "gap"
    assert verdict["invalid"] == ["broken"]
    assert verdict["audio"] is False


def test_evaluate_clear_when_complete():
    snap = {
        "total": 1,
        "valid": 1,
        "stateful": 0,
        "organs": [
            {
                "name": "good",
                "valid": True,
                "contract": {
                    "handler": True,
                    "coherence_vitals": True,
                    "resonates_with": True,
                },
            }
        ],
    }
    verdict = w807.evaluate(snap)
    assert verdict["ok"] is True
    assert verdict["gap_count"] == 0


def test_handler_status_is_silent():
    result = w807.handler({"action": "status"})
    assert result["wave"] == 807
    assert result["surface"] == "sentinel"
    assert result["audio"] is False
    assert "handler" in w807.resonates_with() or "wave806_organ_registry" in w807.resonates_with()
