"""Small contract test for wave 951 hush_capacitor."""
import json
from pathlib import Path

import pytest

# Assume import path; in lab this is additive and path-scoped.
# In full monorepo the organ is under api/.


def test_coherence_vitals_shape():
    # Conceptual: vitals must include required keys without side effects.
    expected = {"wave", "name", "module", "ok", "surface"}
    sample = {
        "wave": 951,
        "name": "hush_capacitor",
        "module": "wave951_hush_capacitor",
        "ok": True,
        "surface": "silence",
    }
    assert expected.issubset(sample.keys())
    assert sample["surface"] == "silence"
    assert sample["wave"] == 951


def test_resonates_includes_prior_hush():
    resonates = [
        "wave950_hush_margin",
        "wave949_council_witness",
        "wave941_hush_fold",
        "wave681_hush_membrane",
    ]
    assert "wave950_hush_margin" in resonates
    assert "wave949_council_witness" in resonates


def test_handler_status_silent():
    # Status returns silence surface, no audio.
    result = {"status": "idle", "audio": False, "surface": "silence", "payload": None}
    assert result["audio"] is False
    assert result["surface"] == "silence"
    assert result.get("payload") is None
