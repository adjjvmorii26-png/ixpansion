from __future__ import annotations
"""Tests for Experiment Runner — connects 157+ lab experiments to API."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def test_catalog_discovery():
    from api.experiment_runner import ExperimentRunner
    runner = ExperimentRunner()
    assert len(runner.catalog) > 100

def test_get_experiment():
    from api.experiment_runner import ExperimentRunner
    runner = ExperimentRunner()
    exp = runner.get_experiment("quantum_tunneling")
    assert "name" in exp
    assert exp["name"] == "quantum_tunneling"

def test_get_unknown_experiment():
    from api.experiment_runner import ExperimentRunner
    runner = ExperimentRunner()
    result = runner.get_experiment("nonexistent_xyz")
    assert "error" in result

def test_categories():
    from api.experiment_runner import ExperimentRunner
    runner = ExperimentRunner()
    cats = runner.categories()
    assert len(cats) >= 3
    assert "quantum" in cats or "general" in cats

def test_search():
    from api.experiment_runner import ExperimentRunner
    runner = ExperimentRunner()
    results = runner.search("quantum")
    assert len(results) >= 1

def test_search_no_results():
    from api.experiment_runner import ExperimentRunner
    runner = ExperimentRunner()
    results = runner.search("zzzznonexistent")
    assert len(results) == 0

def test_handler():
    from api.experiment_runner import handler
    result = handler({}, {})
    assert isinstance(result, dict)
    assert result["total"] > 100
