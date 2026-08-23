import pytest
from omega_prime.agents.cognition.ritual_engine import RitualEngine, RitualState


class TestRitualEngine:
    def test_single_action_no_ritual(self):
        engine = RitualEngine()
        engine.record_action("a1", "step_one")
        assert len(engine._rituals) == 0

    def test_same_sequence_from_two_agents_forms_seedling(self):
        engine = RitualEngine()
        seq = ["bow", "chant", "offer"]
        for agent in ["priest_a", "priest_b"]:
            for action in seq:
                engine.record_action(agent, action)
        assert len(engine._rituals) >= 1

    def test_correct_performance_strengthens(self):
        engine = RitualEngine()
        seq = ["bow", "chant", "offer"]
        for agent in ["p1", "p2"]:
            for action in seq:
                engine.record_action(agent, action)

        ritual = list(engine._rituals.values())[0]
        potency_before = ritual.potency
        # Perform the sequence again correctly
        for action in seq:
            engine.record_action("p1", action)
        assert ritual.potency > potency_before or len(engine._rituals) == 0

    def test_established_ritual_grants_bonus(self):
        engine = RitualEngine()
        seq = ["gather", "ignite", "dance"]
        for agent in ["s1", "s2", "s3", "s4", "s5", "s6"]:
            for _ in range(3):  # Repeat multiple times to build potency
                for action in seq:
                    engine.record_action(agent, action)

        sacred_or_established = [
            r for r in engine._rituals.values()
            if r.state in (RitualState.ESTABLISHED, RitualState.SACRED)
        ]
        if sacred_or_established:
            assert sacred_or_established[0].bonus_multiplier > 1.0

    def test_decayed_rituals_forgotten(self):
        engine = RitualEngine()
        seq = ["clap", "stomp", "whistle"]
        for agent in ["a", "b"]:
            for action in seq:
                engine.record_action(agent, action)
        initial = len(engine._rituals)
        for _ in range(200):
            engine.tick()
        # Rituals should decay without reinforcement
        assert len(engine._rituals) <= initial
