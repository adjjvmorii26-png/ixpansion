import hashlib
import json

import pytest

from lab.astral_network_weaver import register_module
from lab.mycelium_signal import propagate_signal


FIXED_CLOCK = lambda: "2026-08-25T09:00:00+00:00"


def _hash(result):
    material = {k: v for k, v in result.items() if k != "signal_hash"}
    return hashlib.sha256(json.dumps(material, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def test_signal_propagates_through_consuming_chain(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    register_module("source", capabilities=["emit"], clock=FIXED_CLOCK)
    register_module("relay", capabilities=["relay"], consumes=["emit"], clock=FIXED_CLOCK)
    register_module("sink", capabilities=["absorb"], consumes=["relay"], clock=FIXED_CLOCK)
    result = propagate_signal("source", clock=FIXED_CLOCK, record=False)
    assert result["modules_reached"] == 2
    assert result["source"] == "source"
    assert result["execution_enabled"] is False
    assert len(result["trace"]) == 3
    assert result["signal_hash"] == _hash(result)


def test_signal_strength_decays_with_hops(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    register_module("a", capabilities=["x"], clock=FIXED_CLOCK)
    register_module("b", capabilities=["y"], consumes=["x"], clock=FIXED_CLOCK)
    register_module("c", capabilities=["z"], consumes=["y"], clock=FIXED_CLOCK)
    result = propagate_signal("a", hops=3, clock=FIXED_CLOCK, record=False)
    strengths = [t["received_strength"] for t in result["trace"]]
    assert strengths[0] == 1.0
    assert strengths[-1] < strengths[0]


def test_unknown_source_fails(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    with pytest.raises(ValueError, match="unknown source"):
        propagate_signal("ghost", record=False)


def test_recorded_signal_persists(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    register_module("x", capabilities=["emit"], clock=FIXED_CLOCK)
    register_module("y", consumes=["emit"], capabilities=["recv"], clock=FIXED_CLOCK)
    result = propagate_signal("x", clock=FIXED_CLOCK, record=True)
    latest = json.loads((tmp_path / "state" / "mycelium" / "latest_signal.json").read_text())
    assert latest["signal_hash"] == result["signal_hash"]


def test_no_consuming_modules_yields_source_only(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    register_module("lonely", capabilities=["standalone"], clock=FIXED_CLOCK)
    result = propagate_signal("lonely", clock=FIXED_CLOCK, record=False)
    assert result["modules_reached"] == 0
    assert len(result["trace"]) == 1
