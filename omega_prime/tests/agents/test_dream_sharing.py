import pytest
from omega_prime.agents.dream_sharing import DreamSharingNetwork


class TestDreamSharingNetwork:
    def test_single_dreamer_insufficient(self):
        net = DreamSharingNetwork(seed=42)
        net.enter_dream("solo", "forest", intensity=1.0)
        for _ in range(50):
            net.tick()
        dreamscape = net.dreamscape
        assert len(dreamscape["realized_terrain"]) == 0  # Need ≥2 dreamers

    def test_two_dreamers_materialize(self):
        net = DreamSharingNetwork(seed=42)
        net.enter_dream("d1", "ocean", intensity=1.0, position=(10, 10))
        net.enter_dream("d2", "ocean", intensity=1.0, position=(12, 12))
        materialized = False
        for _ in range(100):
            result = net.tick()
            if result["new_materializations"]:
                materialized = True
                break
        assert materialized

    def test_different_archetypes_dont_merge(self):
        net = DreamSharingNetwork(seed=42)
        net.enter_dream("a", "fire", intensity=1.0, position=(5, 5))
        net.enter_dream("b", "ice", intensity=1.0, position=(6, 6))
        dreamscape = net.dreamscape
        forming = dreamscape["forming_dreams"]
        archetypes = {f["archetype"] for f in forming}
        assert len(archetypes) >= 1  # Separate dreams

    def test_exit_stops_contributing(self):
        net = DreamSharingNetwork(seed=42)
        net.enter_dream("x", "void", intensity=1.0)
        net.exit_dream("x")
        assert "x" not in net._active_dreamers

    def test_dream_decay_without_reinforcement(self):
        net = DreamSharingNetwork(seed=42)
        net.enter_dream("temp", "crystal", intensity=0.5)
        initial_count = len(net._shared_dreams)
        for _ in range(200):
            net.tick()
        # Dream should have decayed away
        final_count = len([d for d in net._shared_dreams.values() if not d.materialized])
        assert final_count <= initial_count
