"""Wave 791 lattice_rest tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))

import wave791_lattice_rest as w791


def test_vitals_contract():
    v = w791.coherence_vitals()
    assert v["wave"] == 791
    assert v["name"] == "lattice_rest"
    assert v["ok"] is True
    assert v["surface"] == "silence"
    assert v["audio"] is False
    assert "wave790_still_interval" in w791.resonates_with()


def test_pin_and_find():
    pinned = w791.handler({"action": "pin", "note": "quiet_cell", "seconds": 1.5})
    assert pinned["status"] == "pinned"
    assert pinned["node"]["hash"]
    found = w791.handler({"action": "find", "note": "quiet"})
    assert found["status"] == "found"
    assert found["hits"]
    assert found["audio"] is False
