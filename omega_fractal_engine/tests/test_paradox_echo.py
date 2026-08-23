import pytest
from omega_fractal_engine.meta.paradox_solver import ParadoxSolver, ResolutionStrategy
from omega_fractal_engine.archives.echo_index import EchoIndex


class TestParadoxSolver:
    def test_detect_creates_paradox(self):
        solver = ParadoxSolver()
        p = solver.detect("agent is alive", "agent is dead", support_a=0.8, support_b=0.7)
        assert not p.is_resolved

    def test_sacrifice_weaker_when_clear_winner(self):
        solver = ParadoxSolver()
        p = solver.detect("A is true", "B is true", support_a=0.95, support_b=0.05)
        result = solver.resolve(p)
        assert result["strategy"] == "SACRIFICE_WEAKER"
        assert "A is true" in result["outcome"]

    def test_superposition_when_balanced(self):
        solver = ParadoxSolver()
        p = solver.detect("X", "Y", support_a=0.5, support_b=0.5)
        result = solver.resolve(p)
        assert "SUPERPOSED" in result["outcome"]

    def test_synthesis_when_close(self):
        solver = ParadoxSolver()
        p = solver.detect("hot", "cold", support_a=0.55, support_b=0.45)
        result = solver.resolve(p)
        assert "SYNTHESIS" in result["outcome"]

    def test_stats(self):
        solver = ParadoxSolver()
        p = solver.detect("a", "b", 0.9, 0.1)
        solver.resolve(p)
        stats = solver.stats
        assert stats["resolved"] == 1


class TestEchoIndex:
    def test_remember_and_search(self):
        idx = EchoIndex()
        idx.remember("scout found gold in lattice", "chronicle", tick=1,
                     tags={"lattice", "gold", "discovery"})
        results = idx.search(query_tags={"gold"})
        assert len(results) >= 1
        assert results[0]["relevance"] > 0

    def test_forget(self):
        idx = EchoIndex()
        eid = idx.remember("test", "dream", tick=1, tags={"x"})
        assert idx.forget(eid) is True
        assert idx.forget(eid) is False

    def test_stats(self):
        idx = EchoIndex()
        idx.remember("c", "chronicle", tick=1)
        idx.remember("d", "dream", tick=2)
        stats = idx.stats
        assert stats["total_memories"] == 2
        assert stats["by_source"]["chronicle"] == 1
