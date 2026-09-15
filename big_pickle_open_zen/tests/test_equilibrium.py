"""Tests for equilibrium_field — cross-module balance detection."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import equilibrium_field as ef


def test_coherence_vitals():
    cv = ef.coherence_vitals()
    assert cv["wave"] == 700 and cv["ok"] is True


def test_scan():
    result = ef.handler({"action": "scan", "modules": ["alpha", "beta", "gamma"]})
    assert result["status"] == "scanned"
    assert result["balanced"] + result["imbalanced"] == 3


def test_field():
    ef.handler({"action": "scan", "modules": ["test1", "test2"]})
    field = ef.handler({"action": "field"})
    assert field["status"] == "field"


def test_status():
    st = ef.handler({"action": "status"})
    assert st["status"] == "active" and st["wave"] == 700
