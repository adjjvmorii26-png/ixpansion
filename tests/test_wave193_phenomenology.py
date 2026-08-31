"""Wave 193 — the Phenomenology.

Six organs that give the ecosystem first-person experience: qualia,
liminality, sensory integration, embodied knowledge, diary, and time.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

ORGANS = [
    "qualia_field", "liminal_threshold", "sensory_integration",
    "embodied_knowledge", "phenomenal_record", "temporal_horizon",
]


def test_wave193_organs_are_living():
    from api import coherence_regulator as cr
    living = set(cr._candidate_modules())
    present = [o for o in ORGANS if o in living]
    assert present == ORGANS, f"missing: {set(ORGANS) - set(present)}"


def test_wave193_organs_expose_vitals_and_kinships():
    for name in ORGANS:
        mod = __import__(name)
        assert isinstance(mod.coherence_vitals(), dict), name
        assert isinstance(mod.resonates_with(), list), name


def test_qualia_field_renders():
    from api.qualia_field import _read_qualia
    q = _read_qualia()
    assert "texture" in q
    assert "felt_color" in q
    assert q["organs_felt"] > 100


def test_sensory_integration_fuses():
    from api.sensory_integration import _perception
    p = _perception()
    assert p["signals_fused"] >= 3
    assert "perception" in p


def test_phenomenal_record_writes():
    from api.phenomenal_record import handler
    r = handler({})
    assert r["action"] == "diary"
    assert r["latest"]["mood"] in ("contemplative", "restorative", "fractured")
    assert "diary_entry" in r["latest"]


def test_embodied_knowledge_profiles():
    from api.embodied_knowledge import _body_profile
    p = _body_profile()
    assert p["organs"] > 100
    assert "constitution" in p


def test_temporal_horizon_reads_time():
    from api.temporal_horizon import _time_feeling
    t = _time_feeling()
    assert "temporal_feel" in t
    assert "pulse_frequency_per_minute" in t
