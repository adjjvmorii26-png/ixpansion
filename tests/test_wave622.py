"""Tests for Resilience Mesh (Wave 622)."""
import pytest
from api.wave622_resilience_mesh import (
    OrganHealth, ResilienceMesh, handler, coherence_vitals,
    FAILURE_THRESHOLD,
)


class TestOrganHealth:
    def test_initial_state(self):
        organ = OrganHealth("test_organ")
        assert organ.status == "healthy"
        assert organ.consecutive_failures == 0

    def test_record_success(self):
        organ = OrganHealth("test_organ")
        organ.record_heartbeat(True)
        assert organ.total_successes == 1
        assert organ.status == "healthy"

    def test_record_failure(self):
        organ = OrganHealth("test_organ")
        for _ in range(FAILURE_THRESHOLD):
            organ.record_heartbeat(False)
        assert organ.status == "failing"
        assert organ.consecutive_failures == FAILURE_THRESHOLD

    def test_needs_auto_heal(self):
        organ = OrganHealth("test_organ")
        for _ in range(FAILURE_THRESHOLD):
            organ.record_heartbeat(False)
        assert organ.needs_auto_heal() is True

    def test_trigger_recovery(self):
        organ = OrganHealth("test_organ")
        for _ in range(FAILURE_THRESHOLD):
            organ.record_heartbeat(False)
        entry = organ.trigger_recovery()
        assert entry["action"] == "restart"
        assert organ.recovery_attempts == 1

    def test_needs_heal_after_cooldown(self):
        organ = OrganHealth("test_organ")
        for _ in range(FAILURE_THRESHOLD):
            organ.record_heartbeat(False)
        organ.trigger_recovery()  # first recovery
        organ.last_recovery = 0  # simulate cooldown passed
        assert organ.needs_auto_heal() is True

    def test_no_heal_after_max_attempts(self):
        organ = OrganHealth("test_organ")
        organ.recovery_attempts = 3
        assert organ.needs_auto_heal() is False

    def test_to_dict(self):
        organ = OrganHealth("test_organ")
        d = organ.to_dict()
        assert d["organ_id"] == "test_organ"
        assert "health_score" in d


class TestResilienceMesh:
    def test_register_and_heartbeat(self):
        mesh = ResilienceMesh()
        mesh.register_organ("test")
        result = mesh.heartbeat("test", True)
        assert result["ok"] is True
        assert result["status"] == "healthy"

    def test_heartbeat_failure_detection(self):
        mesh = ResilienceMesh()
        mesh.register_organ("test")
        for _ in range(FAILURE_THRESHOLD):
            mesh.heartbeat("test", False)
        status = mesh.get_organ_status("test")
        assert status["status"] == "failing"

    def test_organism_health(self):
        mesh = ResilienceMesh()
        mesh.register_organ("organ1")
        mesh.register_organ("organ2")
        mesh.heartbeat("organ1", True)
        for _ in range(FAILURE_THRESHOLD):
            mesh.heartbeat("organ2", False)
        health = mesh.get_organism_health()
        assert health["total_organs"] == 2
        assert health["healthy"] == 1
        assert health["failing"] == 1
        assert health["resilience_score"] <= 1.0

    def test_get_failing_organs(self):
        mesh = ResilienceMesh()
        mesh.register_organ("org1")
        for _ in range(FAILURE_THRESHOLD):
            mesh.heartbeat("org1", False)
        failing = mesh.get_failing_organs()
        assert len(failing) == 1
        assert failing[0]["organ_id"] == "org1"

    def test_manual_heal(self):
        mesh = ResilienceMesh()
        mesh.register_organ("org1")
        for _ in range(FAILURE_THRESHOLD):
            mesh.heartbeat("org1", False)
        result = mesh.trigger_manual_heal("org1", "restart")
        assert result["ok"] is True
        assert result["manual"] is True

    def test_history(self):
        mesh = ResilienceMesh()
        mesh.register_organ("org1")
        mesh.heartbeat("org1", True)
        mesh.heartbeat("org1", False)
        hist = mesh.history
        assert len(hist) == 2

    def test_no_organ(self):
        mesh = ResilienceMesh()
        status = mesh.get_organ_status("unknown")
        assert status["ok"] is False


class TestHandler:
    def test_status(self):
        out = handler({"action": "status"})
        assert out["action"] == "status"
        assert out["wave"] == 622
        assert out["total_organs"] > 0

    def test_heartbeat(self):
        out = handler({"action": "heartbeat", "organ_id": "test_org",
                        "healthy": True})
        assert out["action"] == "heartbeat"
        assert out["status"] == "healthy"

    def test_organ_status(self):
        handler({"action": "heartbeat", "organ_id": "status_test",
                 "healthy": True})
        out = handler({"action": "organ_status", "organ_id": "status_test"})
        assert out["status"] == "healthy"

    def test_failing(self):
        handler({"action": "heartbeat", "organ_id": "fail_test",
                 "healthy": False})
        handler({"action": "heartbeat", "organ_id": "fail_test",
                 "healthy": False})
        handler({"action": "heartbeat", "organ_id": "fail_test",
                 "healthy": False})
        out = handler({"action": "failing"})
        failing = [o for o in out["failing_organs"] if o["organ_id"] == "fail_test"]
        assert len(failing) >= 1

    def test_toggle_auto_heal(self):
        out = handler({"action": "toggle_auto_heal"})
        assert out["action"] == "toggle_auto_heal"
        assert "auto_heal_enabled" in out

    def test_history(self):
        out = handler({"action": "history"})
        assert out["action"] == "history"
        assert isinstance(out["history"], list)

    def test_unknown_action(self):
        out = handler({"action": "bogus"})
        assert out["ok"] is False


class TestCoherenceVitals:
    def test_wave(self):
        v = coherence_vitals()
        assert v["wave"] == 622
        assert "total_organs" in v
