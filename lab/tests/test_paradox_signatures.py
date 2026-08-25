import hashlib
import json

import pytest

from lab.paradox_signatures import ingest_paradox, match_paradox, _fingerprint, _cosine_similarity


FIXED_CLOCK = lambda: "2026-08-25T10:00:00+00:00"


def test_ingest_creates_signature(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    paradox = {"identity_collision": 1.0, "risk_index": 0.8, "witnesses": [1, 2, 3]}
    entry = ingest_paradox(paradox, label="test-collision", clock=FIXED_CLOCK)
    assert entry["sig_id"].startswith("sig-")
    assert entry["label"] == "test-collision"
    assert len(entry["features"]) == 10


def test_match_finds_similar(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    p1 = {"identity_collision": 1.0, "state_fork": 0.0, "risk_index": 0.8, "witnesses": [1]}
    p2 = {"identity_collision": 0.9, "state_fork": 0.1, "risk_index": 0.75, "witnesses": [1, 2]}
    ingest_paradox(p1, label="known", clock=FIXED_CLOCK)
    result = match_paradox(p2, threshold=0.5, clock=FIXED_CLOCK)
    assert result["match_count"] == 1
    assert result["matches"][0]["similarity"] > 0.5


def test_no_match_below_threshold(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    p1 = {"identity_collision": 1.0}
    p2 = {"clock_regression": 1.0}
    ingest_paradox(p1, label="a", clock=FIXED_CLOCK)
    result = match_paradox(p2, threshold=0.9, clock=FIXED_CLOCK)
    assert result["match_count"] == 0


def test_fingerprint_is_deterministic():
    p = {"identity_collision": 0.5, "broken_chain": 1.0, "witnesses": [1, 2]}
    assert _fingerprint(p) == _fingerprint(p)


def test_cosine_sim_basic():
    assert _cosine_similarity([1, 0, 0], [1, 0, 0]) == 1.0
    assert _cosine_similarity([1, 0, 0], [0, 1, 0]) == 0.0
