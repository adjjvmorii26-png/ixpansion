"""Waves 774–775 lab tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave774_wave_gap_healer as w774
import wave775_constellation_affinity as w775


def test_774_contract_survey():
    w774.DATA.mkdir(parents=True, exist_ok=True)
    w774.STATE_FILE.write_text(
        '{"wave":774,"name":"wave_gap_healer","surveys":0,"last_gap_count":0,"ghosts":[],"status":"test"}'
    )
    v = w774.coherence_vitals()
    assert v["wave"] == 774
    assert v["policy"] == "survey_not_force_fill"
    r = w774.handler({"action": "survey", "window": 50})
    assert r["status"] == "surveyed"
    assert r["audio"] is False
    assert "gap_count" in r


def test_775_map_pair():
    w775.DATA.mkdir(parents=True, exist_ok=True)
    w775.STATE_FILE.write_text('{"wave":775,"name":"constellation_affinity","maps":0,"status":"test"}')
    v = w775.coherence_vitals()
    assert v["wave"] == 775
    assert v["catalog_size"] >= 10
    m = w775.handler({"action": "map", "seed": "ixpansion"})
    assert m["status"] == "mapped"
    assert m["top"] and m["top"][0]["affinity"] <= 1.0
    p = w775.handler({"action": "pair", "a": "ixpansion", "b": "nexus-observatory"})
    assert 0.0 <= p["affinity"] <= 1.0
    assert p["audio"] is False
