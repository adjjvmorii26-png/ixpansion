"""Tests for Wave 640 — Dependency Resolver."""
import pytest
from api.wave640_dependency_resolver import handler, coherence_vitals, resonates_with

@pytest.fixture(autouse=True)
def clean_state():
    from pathlib import Path
    state = Path("data/wave640_dependency_resolver.json")
    if state.exists():
        state.unlink()
    yield
    if state.exists():
        state.unlink()

class TestHandler:
    def test_status(self):
        r = handler({})
        assert r["ok"] is True
        assert r["tick"] == 0

    def test_scan(self):
        r = handler({"action": "scan"})
        assert r["ok"] is True
        assert "modules_scanned" in r
        assert r["modules_scanned"] > 10

    def test_version_check(self):
        r = handler({"action": "version_check"})
        assert r["ok"] is True
        assert "consistent" in r

    def test_duplicates(self):
        r = handler({"action": "duplicates"})
        assert r["ok"] is True
        assert "duplicate_actions" in r

    def test_resolve(self):
        r = handler({"action": "resolve", "issue_type": "circular_import"})
        assert r["ok"] is True
        assert r["type"] == "circular_import"

    def test_debt_scores_after_scan(self):
        handler({"action": "scan"})
        r = handler({"action": "status"})
        assert r["debt_count"] > 0

    def test_circular_detection_in_scan(self):
        r = handler({"action": "scan"})
        # Circular should be a list (possibly empty)
        assert isinstance(r["circular_imports"], list)

    def test_unknown_action(self):
        r = handler({"action": "xyz"})
        assert r["ok"] is False

class TestCoherenceVitals:
    def test_wave(self):
        v = coherence_vitals()
        assert v["wave"] == 640

class TestResonates:
    def test_list(self):
        r = resonates_with()
        assert "wave639_echo_breaker" in r
        assert "wave622_resilience_mesh" in r
