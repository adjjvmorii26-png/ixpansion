import pytest
from omega_prime.sandbox.modules.physics_evolution import (
    PhysicsGenome, PhysicsEvolutionEngine, FitnessEvaluator,
)


class TestPhysicsGenome:
    def test_mutate_changes_values(self):
        g = PhysicsGenome(gravity=-9.81, friction=0.98)
        child = g.mutate(intensity=0.5)
        assert child.gravity != g.gravity or child.friction != g.friction

    def test_friction_clamped(self):
        g = PhysicsGenome(friction=0.99)
        for _ in range(20):
            child = g.mutate(intensity=1.0)
            assert 0.5 <= child.friction <= 1.0

    def test_crossover_blends(self):
        a = PhysicsGenome(gravity=-1, friction=0.7, time_dilation=0.5,
                          collision_elasticity=0.1, max_velocity=30)
        b = PhysicsGenome(gravity=-100, friction=1.0, time_dilation=5.0,
                          collision_elasticity=0.9, max_velocity=300)
        child = PhysicsGenome.crossover(a, b, bias=0.5)
        assert -100 < child.gravity < -1  # Between parents


class TestFitnessEvaluator:
    def test_high_engagement_scores_well(self):
        ev = FitnessEvaluator()
        score = ev.evaluate({
            "interaction_rate": 0.95,
            "action_diversity": 0.85,
            "stagnation_rate": 0.05,
            "energy_efficiency": 0.8,
        })
        assert score > 0.7

    def test_total_stagnation_scores_zero(self):
        ev = FitnessEvaluator()
        score = ev.evaluate({
            "interaction_rate": 0,
            "action_diversity": 0,
            "stagnation_rate": 1.0,
            "energy_efficiency": 0,
        })
        assert score < 0.1


class TestPhysicsEvolutionEngine:
    def test_initialize_population(self):
        engine = PhysicsEvolutionEngine(seed=42)
        pop = engine.initialize()
        assert len(pop) == 12
        gravities = {g.gravity for g in pop}
        assert len(gravities) > 1  # Diversity

    def test_generation_improves_or_maintains(self):
        engine = PhysicsEvolutionEngine(seed=42)
        pop = engine.initialize()
        scored = [(g, {"interaction_rate": 0.5, "action_diversity": 0.4,
                       "stagnation_rate": 0.3, "energy_efficiency": 0.5}) for g in pop]
        result = engine.submit_generation(scored)
        assert result["generation"] == 1
        assert result["population_size"] == 12

    def test_best_ever_tracking(self):
        engine = PhysicsEvolutionEngine(seed=42)
        pop = engine.initialize()
        scored = [(g, {"interaction_rate": 0.9, "action_diversity": 0.9,
                       "stagnation_rate": 0.05, "energy_efficiency": 0.9}) for g in pop[:6]] + \
                 [(g, {"interaction_rate": 0.1, "action_diversity": 0.1,
                       "stagnation_rate": 0.9, "energy_efficiency": 0.1}) for g in pop[6:]]
        engine.submit_generation(scored)
        best = engine.best_ever
        assert best is not None
        assert best["fitness"] > 0.5
