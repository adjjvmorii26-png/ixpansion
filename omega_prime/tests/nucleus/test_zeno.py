import pytest
from omega_prime.nucleus.kernel.zeno_effect import ZenoField


class TestZenoEffect:
    def test_observation_reduces_freedom(self):
        zeno = ZenoField()
        zeno.register("target")
        initial = zeno._get("target").evolution_freedom
        zeno.observe("watcher", "target")
        after = zeno._get("target").evolution_freedom
        assert after < initial

    def test_unobserved_tick_restores(self):
        zeno = ZenoField()
        zeno.register("a1")
        for _ in range(10):
            zeno.observe("w", "a1")
        frozen_before = zeno._get("a1").evolution_freedom
        for _ in range(20):
            zeno.unobserved_tick("a1")
        after = zeno._get("a1").evolution_freedom
        assert after > frozen_before

    def test_frozen_agent_cannot_mutate(self):
        zeno = ZenoField()
        zeno.register("prisoner")
        for _ in range(15):
            zeno.observe("guard", "prisoner")
        can, reason = zeno.can_mutate("prisoner")
        assert not can

    def test_free_agent_can_mutate(self):
        zeno = ZenoField()
        zeno.register("free_agent")
        can, reason = zeno.can_mutate("free_agent")
        assert can

    def test_stats(self):
        zeno = ZenoField()
        zeno.register("x")
        stats = zeno.tick()
        assert "tracked_agents" in stats and "frozen_agents" in stats

    def test_most_surveilled(self):
        zeno = ZenoField()
        zeno.register("watched")
        zeno.register("ignored")
        for _ in range(5):
            zeno.observe("spy", "watched")
        worst = zeno.most_surveilled
        assert worst is not None
