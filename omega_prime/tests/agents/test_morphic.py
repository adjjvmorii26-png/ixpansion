import pytest
from omega_prime.agents.cognition.morphic_field import MorphicField


class TestMorphicField:
    def test_broadcast_to_same_species(self):
        field = MorphicField()
        field.attune("s1", "sentinel")
        field.attune("s2", "sentinel")
        delivered = field.broadcast("s1", "threat_pattern", {"type": "swarm"})
        assert delivered == 1

    def test_no_cross_species_leak(self):
        field = MorphicField()
        field.attune("s1", "sentinel")
        field.attune("w1", "wanderer")
        delivered = field.broadcast("s1", "key", "val")
        assert delivered == 0

    def test_receive_clears_pending(self):
        field = MorphicField()
        field.attune("s1", "sentinel")
        field.attune("s2", "sentinel")
        field.broadcast("s1", "k", "v")
        echoes = field.receive("s2")
        assert len(echoes) == 1
        assert len(field.receive("s2")) == 0

    def test_coherence_with_single_species(self):
        field = MorphicField()
        field.attune("a", "sentinel")
        field.attune("b", "sentinel")
        assert field.coherence == 1.0
