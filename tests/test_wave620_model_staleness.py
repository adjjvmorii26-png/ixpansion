"""Tests for Wave 620 — Model Staleness Registry."""
from __future__ import annotations

import os
import sys
import time

# ensure api is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))

from model_staleness_registry import (  # noqa: E402
    coherence_vitals,
    handler,
    primary_allowed,
    register_or_update,
    probe_drift,
    sunset_sweep,
    list_models,
    set_frontier,
    TIER_A,
    TIER_B,
    TIER_C,
)


def test_coherence_vitals():
    v = coherence_vitals()
    assert v["wave"] == "620"
    assert v["module"] == "model_staleness_registry"
    assert v["status"] == "active"
    assert "models_tracked" in v


def test_register_and_list():
    r = register_or_update(
        "test/model-fresh",
        release_date="2026-09-01",
        knowledge_cutoff="2026-08",
        notes="unit test model",
    )
    assert r["status"] == "ok"
    assert r["model"]["tier"] == TIER_A
    listed = list_models()
    assert listed["status"] == "ok"
    assert "test/model-fresh" in listed["models"]


def test_probe_drift_demotes():
    register_or_update("test/model-drift", notes="will drift")
    # healthy probe
    p1 = probe_drift("test/model-drift", 0.95, probe_name="healthy")
    assert p1["status"] == "ok"
    assert p1["probe"]["drifted"] is False
    assert p1["model"]["tier"] == TIER_A
    # strong drift -> demote to B
    p2 = probe_drift("test/model-drift", 0.70, probe_name="stale_probe")
    assert p2["status"] == "ok"
    assert p2["probe"]["drifted"] is True
    assert p2["model"]["tier"] == TIER_B


def test_primary_allowed():
    register_or_update("test/primary-ok")
    assert primary_allowed("test/primary-ok") is True
    # force to C
    register_or_update("test/primary-bad", force_tier=TIER_C)
    assert primary_allowed("test/primary-bad") is False


def test_handler_actions():
    st = handler({"action": "status"})
    assert st["wave"] == "620"
    lst = handler({"action": "list"})
    assert lst["status"] == "ok"
    reg = handler({"action": "register", "model": "test/handler-model", "notes": "via handler"})
    assert reg["status"] == "ok"
    pr = handler({"action": "probe", "model": "test/handler-model", "relative_score": 0.99})
    assert pr["status"] == "ok"
    sun = handler({"action": "sunset"})
    assert sun["status"] == "ok"
    allowed = handler({"action": "primary_allowed", "model": "test/handler-model"})
    assert allowed["allowed"] is True


def test_set_frontier():
    register_or_update("test/frontier-candidate")
    r = set_frontier("test/frontier-candidate")
    assert r["status"] == "ok"
    assert r["frontier_reference"] == "test/frontier-candidate"
    listed = list_models()
    assert listed["frontier_reference"] == "test/frontier-candidate"
