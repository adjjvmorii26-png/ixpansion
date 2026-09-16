"""Tests for Wave 757 — axiom_mutator."""
from __future__ import annotations

from api.wave757_axiom_mutator import NAME, WAVE, _DEFAULT_AXIOMS, coherence_vitals, handler, resonates_with


def test_contract():
    assert callable(handler) and callable(coherence_vitals)
    assert isinstance(resonates_with(), list)


def test_ping():
    assert handler({"action": "ping"})["ok"]


def test_status():
    out = handler({"action": "status"})
    assert out["ok"] and out["wave"] == WAVE


def test_axioms_returns_defaults():
    out = handler({"action": "axioms"})
    assert out["ok"]
    for key in _DEFAULT_AXIOMS:
        assert key in out["axioms"]


def test_rewrite():
    out = handler({"action": "rewrite", "key": "module", "value": "A living process."})
    assert out["ok"] and out["rewritten_to"] == "A living process."
    ax = handler({"action": "axioms"})["axioms"]
    assert ax["module"] == "A living process."


def test_revert():
    handler({"action": "rewrite", "key": "module", "value": "test"})
    out = handler({"action": "revert", "key": "module"})
    assert out["ok"] and out["reverted_to"] == _DEFAULT_AXIOMS["module"]


def test_revert_unknown_key():
    out = handler({"action": "revert", "key": "nonexistent"})
    assert out["ok"] is False and out["error"] == "no_default_for_key"


def test_history():
    handler({"action": "rewrite", "key": "wave", "value": "A dream the organism dreams."})
    out = handler({"action": "history"})
    assert out["ok"] and out["total"] >= 1


def test_unknown_action():
    assert handler({"action": "nope"})["ok"] is False


def test_coherence_vitals():
    v = coherence_vitals()
    assert v["wave"] == WAVE and v["status"] == "active" and v["axioms"] >= 5
