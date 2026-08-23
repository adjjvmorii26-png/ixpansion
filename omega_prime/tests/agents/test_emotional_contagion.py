import pytest
from omega_prime.agents.cognition.emotional_contagion import (
    EmotionalContagionNetwork, EmotionalState,
)


class TestEmotionalState:
    def test_classification(self):
        assert EmotionalState(valence=0.8, arousal=0.9).classify() == "ecstatic"
        assert EmotionalState(valence=-0.8, arousal=0.9).classify() == "panicked"
        assert EmotionalState(valence=0.0, arousal=0.3).classify() == "neutral"

    def test_contagious_threshold(self):
        calm = EmotionalState(valence=0.1, arousal=0.2)
        excited = EmotionalState(valence=0.8, arousal=0.9)
        assert not calm.is_contagious
        assert excited.is_contagious


class TestEmotionalContagion:
    def test_emotion_spreads_to_nearby(self):
        net = EmotionalContagionNetwork()
        net.set_emotion("panicked", valence=-0.9, arousal=0.95)
        net.set_emotion("calm_neighbor", valence=0.2, arousal=0.2)
        net.set_position("panicked", (0, 0))
        net.set_position("calm_neighbor", (2, 2))
        result = net.tick()
        assert result["transfers_this_tick"] >= 1

    def test_distant_agents_no_transfer(self):
        net = EmotionalContagionNetwork()
        net.set_emotion("far_source", valence=-0.9, arousal=0.95)
        net.set_emotion("far_target", valence=0.0, arousal=0.3)
        net.set_position("far_source", (0, 0))
        net.set_position("far_target", (100, 100))
        result = net.tick()
        assert result["transfers_this_tick"] == 0

    def test_emotional_weather(self):
        net = EmotionalContagionNetwork()
        for i in range(10):
            net.set_emotion(f"a{i}", valence=0.6, arousal=0.4)
        weather = net.emotional_weather
        assert weather["climate"] in ("serene", "jubilant", "calm")
        assert weather["valence"] > 0

    def test_decay_over_time(self):
        net = EmotionalContagionNetwork()
        net.set_emotion("agent", valence=0.9, arousal=0.9)
        initial_val = net._states["agent"].valence
        for _ in range(50):
            net.tick()
        final_val = net._states["agent"].valence
        assert abs(final_val) < abs(initial_val)
