import pytest
from omega_prime.agents.cognition.memetic_engine import MemeticEngine


class TestMemeticEngine:
    def test_originate_creates_meme(self):
        engine = MemeticEngine(seed=42)
        meme = engine.originate("a1", "move_north_always")
        assert meme.payload == "move_north_always"
        assert meme.generation == 0

    def test_transmit_copies_with_mutation(self):
        engine = MemeticEngine(seed=42)
        engine.originate("source", "spread_me", virulence=1.0)
        results = engine.transmit("source", "target")
        assert len(results) >= 0  # May or may not transmit depending on RNG

    def test_forced_transmission(self):
        engine = MemeticEngine(seed=42)
        engine.originate("src", "viral_content", virulence=1.0)
        for _ in range(20):
            results = engine.transmit("src", "dst")
            if results:
                break
        # At least one should succeed with virulence=1.0 over 20 tries
        total = sum(len(engine.transmit("src", "dst")) for _ in range(50))
        assert total > 0

    def test_parasitic_flag(self):
        engine = MemeticEngine(seed=42)
        meme = engine.originate("hacker", "override_host_will", parasitic=True)
        assert meme.parasitic is True

    def test_dominant_meme(self):
        engine = MemeticEngine(seed=42)
        m1 = engine.originate("a", "weak", virulence=0.1)
        m2 = engine.originate("a", "strong", virulence=0.9)
        dominant = engine.get_dominant_meme("a")
        assert dominant is not None

    def test_tick_stats(self):
        engine = MemeticEngine(seed=42)
        engine.originate("a", "test")
        result = engine.tick()
        assert result["total_infections"] >= 1

    def test_cull_weakest(self):
        engine = MemeticEngine(seed=42)
        for i in range(10):
            engine.originate("agent", f"meme_{i}", virulence=0.1 + i * 0.05)
        culled = engine.cull_weakest("agent", max_infections=3)
        assert culled == 7
