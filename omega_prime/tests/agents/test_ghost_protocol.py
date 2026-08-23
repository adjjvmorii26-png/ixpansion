import pytest
from omega_prime.agents.ghost_protocol import GhostProtocol


class TestGhostProtocol:
    def test_enter_ghost_state(self):
        gp = GhostProtocol()
        record = gp.enter_ghost_state("a1", "sentinel")
        assert "a1" in gp.active_ghosts

    def test_exit_returns_knowledge(self):
        gp = GhostProtocol()
        gp.enter_ghost_state("a1", "scout")
        gp.ghost_observe("a1", {"insight": "gold_at_north", "tick": 5})
        result = gp.exit_ghost_state("a1")
        assert result is not None
        assert "gold_at_north" in result["bonus_knowledge"]
        assert "a1" not in gp.active_ghosts

    def test_exit_nonexistent_returns_none(self):
        gp = GhostProtocol()
        assert gp.exit_ghost_state("nobody") is None

    def test_whisper_and_drain(self):
        gp = GhostProtocol()
        gp.enter_ghost_state("g1", "wanderer")
        assert gp.whisper("g1", "danger_east", target_species="sentinel") is True
        hints = gp.drain_whispers("sentinel")
        assert "danger_east" in hints
        assert len(gp.drain_whispers("sentinel")) == 0  # Drained

    def test_whisper_species_filtered(self):
        gp = GhostProtocol()
        gp.enter_ghost_state("g1", "wanderer")
        gp.whisper("g1", "secret", target_species="architect")
        sentinel_hints = gp.drain_whispers("sentinel")
        assert "secret" not in sentinel_hints

    def test_stats(self):
        gp = GhostProtocol()
        gp.enter_ghost_state("x", "y")
        stats = gp.stats
        assert stats["ghost_count"] == 1
