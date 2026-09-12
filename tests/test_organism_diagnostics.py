"""Tests for Organism Diagnostics Sweep."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
import organism_diagnostics as od

def test_sweep_returns_health():
    r = od.run_sweep()
    assert "health_score" in r
    assert 0 <= r["health_score"] <= 100

def test_sweep_has_summary():
    r = od.run_sweep()
    s = r["summary"]
    assert "total_files" in s
    assert "healthy" in s
    assert "stale" in s
    assert "corrupted" in s
    assert s["total_files"] > 0

def test_sweep_has_modules():
    r = od.run_sweep()
    assert isinstance(r["modules"], list)
    assert len(r["modules"]) > 0

def test_classify():
    assert od._classify("paradox_echo") == "metaphysical"
    assert od._classify("organism_name") == "organism_core"
    assert od._classify("wave_seeds") == "wave_seed"
    assert od._classify("bloom") == "general"

def test_diagnostic_report_persists():
    r = od.run_sweep()
    report_path = Path(__file__).parent.parent / "data" / "diagnostic_report.json"
    assert report_path.exists()
    import json
    report = json.loads(report_path.read_text())
    assert "health_score" in report
    assert "anomalies" in report

def test_summary_action():
    r = od.handler({"action": "summary"})
    assert "health_score" in r
    assert "summary" in r

def test_anomaly_structure():
    r = od.run_sweep()
    for a in r["anomalies"][:3]:
        assert "type" in a
        assert "file" in a
