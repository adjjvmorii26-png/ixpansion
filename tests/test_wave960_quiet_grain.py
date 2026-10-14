"""Contract tests for wave960_quiet_grain. Lab gate only."""
import json
from pathlib import Path

import pytest

from api.wave960_quiet_grain import (
    coherence_vitals,
    handler,
    resonates_with,
    STATE_FILE,
)


def test_handler_increments_without_audio(tmp_path, monkeypatch):
    monkeypatch.setattr("api.wave960_quiet_grain.STATE_FILE", tmp_path / "w960.json")
    r1 = handler()
    assert r1["ok"] is True
    assert r1["grains"] == 1
    assert r1["audio"] is False
    assert r1["surface"] == "silence"
    r2 = handler()
    assert r2["grains"] == 2


def test_coherence_vitals_silence_surface():
    v = coherence_vitals()
    assert v["wave"] == 960
    assert v["ok"] is True
    assert v["surface"] == "silence"
    assert "grains" in v


def test_resonates_with_prior_hush():
    names = resonates_with()
    assert "wave959_micro_ash" in names
    assert isinstance(names, list)
