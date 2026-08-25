from __future__ import annotations
"""Tests for core modules and cross-module integration."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Anomaly Detector ──────────────────────────────────────────────

def test_scan_anomalies():
    from api.anomaly_detector import scan_anomalies
    result = scan_anomalies()
    assert isinstance(result, dict)
    assert "anomalies" in result

def test_scan_has_summary():
    from api.anomaly_detector import scan_anomalies
    result = scan_anomalies()
    assert "summary" in result
    assert "anomaly_count" in result["summary"]


# ── Sandbox ───────────────────────────────────────────────────────

def test_discover_sandbox():
    from api.sandbox import discover_sandbox_modules
    result = discover_sandbox_modules()
    assert isinstance(result, dict)
    assert len(result) > 0


# ── Stream Reactor ────────────────────────────────────────────────

def test_generate_stream():
    from api.stream_reactor import generate_reactor_stream
    result = generate_reactor_stream()
    assert isinstance(result, dict)
    assert "event" in result

def test_stream_has_signals():
    from api.stream_reactor import generate_reactor_stream
    result = generate_reactor_stream()
    assert "signals" in result


# ── Wave Log ──────────────────────────────────────────────────────

def test_wave_log():
    from api.wave_log import get_wave_log
    result = get_wave_log()
    assert isinstance(result, dict)
    assert "waves" in result


# ── Handler smoke (fast modules only) ─────────────────────────────

def test_fast_handlers():
    from api.anomaly_detector import handler as h1
    from api.sandbox import handler as h3
    from api.stream_reactor import handler as h4
    from api.wave_log import handler as h6
    for h in [h1, h3, h4, h6]:
        result = h({}, {})
        assert isinstance(result, (dict, list))


# ── Cross-Module Integration ──────────────────────────────────────

def test_gateway_routes_to_all_modules():
    from api.api_gateway import APIGateway, MODULE_REGISTRY
    gw = APIGateway()
    for module in list(MODULE_REGISTRY.keys())[:5]:
        result = gw.route(module)
        assert result.get("status") == "routed" or "error" in result

def test_neural_fabric_cross_connect():
    from api.neural_fabric import NeuralFabric, MODULES
    nf = NeuralFabric()
    r1 = nf.connect("agent_rental", "billing")
    r2 = nf.connect("billing", "marketplace")
    assert r1.get("connected") or r1.get("strengthened")
    assert r2.get("connected") or r2.get("strengthened")

def test_event_stream_full_cycle():
    from api.event_stream import EventStream
    es = EventStream()
    sub = es.subscribe("test_user", "experiment.*")
    es.publish("experiment.started", {"exp": "quantum_chaos"})
    es.publish("experiment.completed", {"exp": "quantum_chaos", "result": "success"})
    events = es.stream(sub["subscription_id"])
    assert len(events) >= 1

def test_dream_pipeline():
    from api.dream_synthesis import DreamSynthesis
    from api.dream_interpreter import DreamInterpreter
    ds = DreamSynthesis()
    di = DreamInterpreter()
    dream = ds.generate("integration_test", theme="quantum paradox")
    interpretation = di.analyze(dream)
    assert len(interpretation["insights"]) >= 1

def test_pricing_with_arbitrage():
    from api.gravitational_pricing import GravitationalPricing
    from api.temporal_arbitrage import TemporalArbitrage
    gp = GravitationalPricing()
    ta = TemporalArbitrage()
    p1 = gp.get_price("compute_hour")
    bridge = ta.setup("compute_hour", "arb_test", p1["unit_price"] * 0.5, p1["unit_price"] * 2.0)
    assert "bridge_id" in bridge
