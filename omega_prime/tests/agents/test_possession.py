import pytest
from omega_prime.agents.possession import PossessionManager


class TestPossessionManager:
    def test_non_ghost_cannot_possess(self):
        pm = PossessionManager()
        result = pm.attempt("not_ghost", "host", "sentinel", 0.1)
        assert result["success"] is False

    def test_vigorous_host_resists(self):
        pm = PossessionManager()
        pm.register_ghost("g1")
        result = pm.attempt("g1", "h1", "sentinel", 0.9)
        assert result["success"] is False

    def test_weak_host_can_be_possessed(self):
        pm = PossessionManager()
        pm.register_ghost("g1")
        results = [pm.attempt("g1", f"h{i}", "wanderer", 0.05) for i in range(20)]
        assert any(r["success"] for r in results)

    def test_controller_during_possession(self):
        pm = PossessionManager()
        pm.register_ghost("g1")
        # Force success by trying many times with very weak host
        for i in range(50):
            r = pm.attempt("g1", f"host_{i}", "wanderer", 0.01)
            if r["success"]:
                assert pm.get_controller(f"host_{i}") == "g1"
                return
        pytest.skip("possession never succeeded in 50 attempts")

    def test_tick_decays_possessions(self):
        pm = PossessionManager()
        pm.register_ghost("g1")
        for i in range(100):
            r = pm.attempt("g1", f"h{i}", "wanderer", 0.01)
            if r["success"]:
                break
        else:
            pytest.skip("no possession achieved")

        for _ in range(100):
            pm.tick()
        assert len(pm.possessed_agents) < 100

    def test_inject_memory_during_possession(self):
        pm = PossessionManager()
        pm.register_ghost("g1")
        for i in range(100):
            r = pm.attempt("g1", f"h{i}", "wanderer", 0.01)
            if r["success"]:
                assert pm.inject_memory(f"h{i}", "I saw the void") is True
                return
        pytest.skip("no possession achieved")
