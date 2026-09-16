"""Contract tests for Ouroboros-dreamed waves 710-714."""
from __future__ import annotations
import importlib
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

DREAM_WAVES = list(range(710, 720))
MODULE = "wave{}_rift_quill_span_f745"

@pytest.mark.parametrize("wave", DREAM_WAVES)
def test_dream_wave_contract(wave):
    mod = importlib.import_module(MODULE.format(wave))
    v = mod.coherence_vitals()
    assert v["ok"] is True
    assert v["wave"] == wave
    assert v["spawned_by"] == "ouroboros"

@pytest.mark.parametrize("wave", DREAM_WAVES)
def test_dream_wave_actions(wave):
    mod = importlib.import_module(MODULE.format(wave))
    status = mod.handler({"action": "status"})
    assert status["status"] == "dreaming"
    assert status["wave"] == wave
    assert status["ok"] is True
    awakened = mod.handler({"action": "awaken"})
    assert awakened["status"] == "awakened"
    assert awakened["wave"] == wave

@pytest.mark.parametrize("wave", DREAM_WAVES)
def test_dream_wave_resonates(wave):
    mod = importlib.import_module(MODULE.format(wave))
    assert "ouroboros" in mod.resonates_with()

def test_dream_wave_unknown_action():
    mod = importlib.import_module(MODULE.format(710))
    r = mod.handler({"action": "nonsense"})
    assert r["status"] == "unknown_action"
