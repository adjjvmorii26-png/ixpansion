"""Tests for Wave 767 — mycelial_truths."""
from pathlib import Path

import pytest

from api.wave767_mycelial_truths import (
    handler, coherence_vitals, resonates_with,
    SETTLE_EVIDENCE, DATA_FILE, _confidence, _belief_key,
)


@pytest.fixture(autouse=True)
def _isolate_state():
    """Snapshot the living data file so each test sees the same seed."""
    blob = DATA_FILE.read_bytes() if DATA_FILE.exists() else None
    yield
    if blob is None:
        if DATA_FILE.exists():
            DATA_FILE.unlink()
    else:
        DATA_FILE.write_bytes(blob)


def test_contract():
    v = coherence_vitals()
    assert v["wave"] == 767
    assert v["name"] == "mycelial_truths"
    assert v["status"] == "active"
    assert "module_health" in v
    assert v["settled_truths"] >= 0


def test_resonates():
    kins = resonates_with()
    assert "epoch_engine" in kins
    assert "axiom_mutator" in kins


def test_status():
    r = handler({"action": "status"})
    assert "beliefs" in r
    assert "settled_truths" in r
    assert "mycelial_links" in r


def test_truths_sorted():
    r = handler({"action": "truths"})
    confidences = [b["confidence"] for b in r["truths"]]
    assert confidences == sorted(confidences, reverse=True)


def test_propose():
    r = handler({"action": "propose", "subject": "proposal_subject", "predicate": "proposals gestate"})
    assert r["belief"]["status"] == "gestating"
    if r.get("born") is False or "already gestating" in r.get("note", ""):
        # state restored by fixture, so this should be a fresh birth
        assert False, "proposal subject should not pre-exist"


def test_observe_settles():
    r = handler({"action": "observe", "subject": "dream_compiler", "predicate": "dreams become code"})
    assert r["status"] in ("gestating", "settled")
    assert r["evidence"] >= 1


def test_observe_subject_only_reinforces_strongest():
    r = handler({"action": "observe", "subject": "epoch_engine"})
    assert r["status"] in ("gestating", "settled")
    assert r["evidence"] >= 1


def test_consensus_settles_threshold():
    # lore proposal arrives gestating but pre-evidenced; consensus settles it
    handler({"action": "propose", "subject": "consensus_probe", "predicate": "many witnesses make truth heavy",
             "evidence": SETTLE_EVIDENCE + 1})
    r = handler({"action": "consensus"})
    assert any("consensus_probe" in key for key in r["settled"])
    s = handler({"action": "truths", "subject": "consensus_probe"})
    assert s["truths"][0]["status"] == "settled"


def test_entangle():
    r = handler({"action": "entangle", "left": "dream_compiler", "right": "recursive_genesis"})
    assert r["count"] >= 1


def test_influence():
    r = handler({"action": "influence"})
    assert r["count"] >= 3          # seeded settled truths
    for p in r["pressures"]:
        assert p["mutation_pressure"] > 0


def test_challenge_thin_truth_overturns():
    # craft a barely-settled truth
    handler({"action": "propose", "subject": "fragile_truth", "predicate": "is barely held"})
    for _ in range(SETTLE_EVIDENCE):
        handler({"action": "observe", "subject": "fragile_truth", "predicate": "is barely held"})
    r = handler({"action": "challenge", "subject": "fragile_truth", "predicate": "is barely held"})
    assert r["outcome"] == "overturned"
    assert r["belief"]["status"] == "overturned"


def test_unknown_action():
    r = handler({"action": "nonsense"})
    assert "error" in r


def test_confidence_saturates():
    assert _confidence(1) < _confidence(SETTLE_EVIDENCE)
    assert _confidence(100) < 1.0


def test_belief_key():
    assert _belief_key({"subject": "a", "predicate": "b"}) == "a::b"
