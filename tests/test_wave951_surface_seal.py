"""Focused test for wave951 surface_seal.

Lab gate only. Does not exercise ALEPH CI.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from api.wave951_surface_seal import handler, coherence_vitals, resonates_with


def test_contract():
    vitals = coherence_vitals()
    assert vitals["wave"] == 951
    assert vitals["ok"] is True
    assert vitals["surface"] == "silence"
    assert "wave950_hush_margin" in resonates_with()


def test_seal_and_caption():
    out = handler({"action": "seal", "margin": 3, "token": "abc123def456"})
    assert out["status"] == "sealed"
    assert out["audio"] is False
    assert out["payload"] is None
    assert len(out.get("token") or "") == 10
    assert "surface seal" in out.get("caption", "")

    cap = handler({"action": "caption"})
    assert cap["status"] == "captioned"
    assert cap["audio"] is False
    assert "product surface" in cap.get("caption", "")


def test_status_silent():
    st = handler({"action": "status"})
    assert st["audio"] is False
    assert st["surface"] == "silence"
    assert st["wave"] == 951


if __name__ == "__main__":
    test_contract()
    test_seal_and_caption()
    test_status_silent()
    print("wave951 tests ok")
