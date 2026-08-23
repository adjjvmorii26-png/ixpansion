import pytest
from omega_prime.sandbox.modules.ontological_collapse import OntologicalCollapseEngine


class TestOntologicalCollapse:
    def test_below_threshold_no_cascade(self):
        engine = OntologicalCollapseEngine(seed=42)
        for i in range(3):
            engine.add_ambiguity((i, 0), {"a", "b"})
        result = engine.tick()
        assert result["cascade"] is False

    def test_above_threshold_triggers_cascade(self):
        engine = OntologicalCollapseEngine(seed=42)
        # Add enough ambiguous cells to exceed 60% ratio
        for i in range(10):
            engine.add_ambiguity((i, 0), {"x", "y", "z"})
        engine.resolve_cell_manually((100, 100), "solid")  # 1 consolidated vs 10 ambiguous
        result = engine.tick()
        assert result["cascade"] is True
        assert result["cells_resolved"] == 10

    def test_shock_affects_nearby_agents(self):
        engine = OntologicalCollapseEngine(seed=42)
        engine.register_agent_position("nearby", (2.0, 0.0))
        for i in range(10):
            engine.add_ambiguity((i, 0), {"p", "q"})
        result = engine.tick()
        assert result["cascade"] is True
        assert len(result["shocked_agents"]) >= 1

    def test_all_cells_consolidated_after_cascade(self):
        engine = OntologicalCollapseEngine(seed=42)
        for i in range(8):
            engine.add_ambiguity((i, 0), {"a", "b"})
        engine.resolve_cell_manually((50, 50), "fixed")
        engine.tick()
        assert len(engine._ambiguity_map) == 0
        assert len(engine._consolidated) == 9

    def test_stats(self):
        engine = OntologicalCollapseEngine(seed=42)
        stats = engine.stats
        assert "ambiguity_ratio" in stats and "is_critical" in stats
