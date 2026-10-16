"""Tests for wave963 quiet_seam organ. Lab gates only."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from api.wave963_quiet_seam import (
    coherence_vitals,
    handler,
    resonates_with,
    STATE_FILE,
)


@pytest.fixture(autouse=True)
def isolate_state(tmp_path, monkeypatch):
    state = tmp_path / "wave963_quiet_seam.json"
    monkeypatch.setattr("api.wave963_quiet_seam.STATE_FILE", state)
    monkeypatch.setattr("api.wave963_quiet_seam.DATA", tmp_path)
    yield


def test_status_idle():
    out = handler({"action": "status"})
    assert out["ok"] is True
    assert out["wave"] == 963
    assert out["seams"] == 0


def test_seam_creates_token():
    out = handler({"action": "seam", "grain": "unsaid", "fossil": "hush"})
    assert out["ok"] is True
    assert len(out["seam"]) == 12
    assert out["seams"] == 1


def test_vitals_and_resonance():
    handler({"action": "seam", "grain": "a", "fossil": "b"})
    vitals = coherence_vitals()
    assert vitals["ok"] is True
    assert vitals["surface"] == "silence"
    assert vitals["seams"] == 1
    assert 0.62 < vitals["resonance"] < 0.7


def test_resonates_with_prior():
    links = resonates_with()
    assert "wave962_hush_fossil" in links
    assert len(links) >= 2


def test_unknown_action():
    out = handler({"action": "nope"})
    assert out["ok"] is False
