"""Wave 139 — Platform & Live Serving Layer tests."""
import sys
import os
import json
import threading
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))

from uptime_monitor import UptimeMonitor
from metrics_exporter import MetricsExporter
from runtime_config import RuntimeConfig
from route_registry import RouteRegistry
from cache_manager import CacheManager
from endpoint_docs import EndpointDocs
from platform_pulse import PlatformPulse
from deployment_log import DeploymentLog


def test_wave139_uptime_monitor():
    um = UptimeMonitor(target=0.99)
    um.record_request(True)
    um.record_request(True)
    assert um.availability() == 1.0
    um.record_request(False)
    assert um.availability() < 1.0
    assert um.status()["degraded"]
    assert um.status()["blips"] >= 1


def test_wave139_metrics_exporter():
    me = MetricsExporter()
    me.record("router", 0.1, ok=True)
    me.record("router", 0.2, ok=True)
    me.record("ledger", 0.5, ok=False)
    assert me.avg_latency("router") > 0.1
    assert me.error_rate("ledger") == 1.0
    assert "ixpansion_module_hits" in me.prometheus()
    assert me.status()["modules_tracked"] == 2


def test_wave139_runtime_config():
    rc = RuntimeConfig(env={"NEXUS_MODE": "production", "NEXUS_SEED": "7",
                            "NEXUS_WAVE": "142", "NEXUS_MODULES": "351",
                            "NEXUS_ROUTES": "7"})
    assert rc.mode() == "production"
    assert rc.seed() == 7
    checks = rc.validate(actual_modules=351, actual_routes=7)
    assert checks["modules_match"]
    assert checks["routes_match"]
    assert rc.status()["wave"] == "142"


def test_wave139_route_registry():
    rr = RouteRegistry()
    assert rr.count() >= 1
    assert "api/index.py" in rr.destinations()
    assert rr.status()["routes"] >= 1


def test_wave139_cache_manager():
    cm = CacheManager(ttl_s=100.0, max_entries=100)
    assert cm.get("a") is None
    cm.put("a", {"value": 1})
    assert cm.get("a") == {"value": 1}
    for i in range(120):
        cm.put(f"key{i}", i)
    assert cm.status()["entries"] <= 100  # bounded
    assert cm.hit_rate() > 0


def test_wave139_endpoint_docs():
    ed = EndpointDocs()
    entry = ed.scan_module("workforce_orchestrator")
    assert entry["handler"] is True
    assert ed.status()["documented"] >= 1


def test_wave139_platform_pulse():
    pp = PlatformPulse()
    s1 = pp.measure(uptime=0.99, available_modules=351, cache_health=0.9, config_valid=True)
    s2 = pp.measure(uptime=0.5, available_modules=50, cache_health=0.2, config_valid=False)
    assert s2 < s1
    assert pp.trend() < 0
    assert pp.status()["samples"] >= 2


def test_wave139_deployment_log():
    dl = DeploymentLog()
    entry = dl.record("3.55.0", "139", commit="test")
    assert entry["version"] == "3.55.0"
    assert dl.latest()["version"] == "3.55.0"
    assert dl.status()["deployments"] >= 1


def test_wave139_server_live():
    """Boot the live server on an ephemeral port and hit it."""
    import api_server
    server = api_server.create_server(port=0)  # ephemeral port
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urllib.request.urlopen(f"http://localhost:{port}/health", timeout=10) as resp:
            body = json.loads(resp.read().decode())
        assert body["status"] == "healthy"
        assert int(body["wave"]) >= 139
        with urllib.request.urlopen(f"http://localhost:{port}/api/revenue_orchestrator", timeout=10) as resp:
            mod = json.loads(resp.read().decode())
        assert mod["module"] == "revenue_orchestrator"
        with urllib.request.urlopen(f"http://localhost:{port}/modules", timeout=10) as resp:
            modules = json.loads(resp.read().decode())
        assert modules["count"] >= 300
    finally:
        server.shutdown()


def test_wave139_handlers():
    from uptime_monitor import handler as h1
    from metrics_exporter import handler as h2
    from runtime_config import handler as h3
    from route_registry import handler as h4
    from cache_manager import handler as h5
    from endpoint_docs import handler as h6
    from platform_pulse import handler as h7
    from deployment_log import handler as h8
    for h in (h1, h2, h3, h4, h5, h6, h7, h8):
        r = h({})
        assert r["status"] == "active"
