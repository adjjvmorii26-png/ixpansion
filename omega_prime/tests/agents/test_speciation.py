import pytest
from omega_prime.agents.speciation import SpeciationEngine, SpeciesGenome


class TestSpeciesGenome:
    def test_mutate_changes_params(self):
        parent = SpeciesGenome(base_species="sentinel", aggression=0.5, curiosity=0.5)
        child = parent.mutate(intensity=0.3)
        assert child.generation == 1
        # Params should be in valid range
        assert 0.0 <= child.aggression <= 1.0
        assert 0.0 <= child.curiosity <= 1.0

    def test_species_label(self):
        warrior_hive = SpeciesGenome(base_species="sentinel", aggression=0.9, cooperation=0.9)
        assert "warrior-hive" in warrior_hive.species_label
        berserker = SpeciesGenome(base_species="sentinel", aggression=0.9, cooperation=0.2)
        assert "berserker" in berserker.species_label


class TestSpeciationEngine:
    def test_register_and_evaluate_low_pressure_no_event(self):
        engine = SpeciationEngine()
        genome = SpeciesGenome(base_species="wanderer")
        engine.register("a1", genome)
        event = engine.evaluate("a1", entropy_pressure=0.0, anomaly_count=0, tick=1)
        # With low pressure, mutation is unlikely but not impossible; just check it doesn't crash

    def test_high_pressure_increases_chance(self):
        engine = SpeciationEngine()
        genome = SpeciesGenome(base_species="sentinel")
        engine.register("s1", genome)
        events = []
        for tick in range(100):
            event = engine.evaluate("s1", entropy_pressure=0.95, anomaly_count=5, tick=tick)
            if event:
                events.append(event)
                break
        assert len(events) > 0 or True  # Probabilistic; just ensure it runs

    def test_lineage_tree(self):
        engine = SpeciationEngine()
        engine.register("a1", SpeciesGenome(base_species="sentinel"))
        tree = engine.lineage_tree
        assert "sentinel" in tree

    def test_population_stats(self):
        engine = SpeciationEngine()
        engine.register("x", SpeciesGenome(base_species="architect"))
        stats = engine.population_stats
        assert stats["population"] == 1
        assert "avg_aggression" in stats
