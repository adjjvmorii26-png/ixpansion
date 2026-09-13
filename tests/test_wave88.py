"""Tests for Wave 88 — Cross-realm Coherence Bridges."""
import pytest
from pathlib import Path
from api.wave88_cross_realm_bridges import (
    CoherenceBridge, CrossRealmCoherenceLattice, coherence_vitals, handler,
)


class TestCoherenceBridge:
    def test_transmit(self):
        bridge = CoherenceBridge("gradient", "regulation", "test_bridge")
        result = bridge.transmit({"message": "test"}, strength=0.8)
        assert result["status"] == "transmitted"
        assert result["strength"] == 0.8
        assert len(bridge.message_history) == 1

    def test_receive(self):
        bridge = CoherenceBridge("gradient", "regulation", "test_bridge")
        bridge.transmit({"msg": "hello"})
        result = bridge.receive({"msg": "hello"}, strength=0.6)
        assert result["status"] == "received"
        assert result["strength"] == 0.6

    def test_inactive_bridge(self):
        bridge = CoherenceBridge("gradient", "regulation", "test_bridge")
        bridge.active = False
        result = bridge.transmit({"msg": "test"})
        assert result["status"] == "bridge_inactive"


class TestCrossRealmCoherenceLattice:
    def test_init(self):
        lattice = CrossRealmCoherenceLattice()
        assert len(lattice.subsystems) == 3
        assert len(lattice.bridges) == 6  # 3*2 directed bridges

    def test_connect(self):
        lattice = CrossRealmCoherenceLattice()
        result = lattice.connect("gradient", "regulation", strength=0.7)
        assert result["status"] == "bridge_activated"
        assert result["strength"] == 0.7

    def test_broadcast(self):
        lattice = CrossRealmCoherenceLattice()
        results = lattice.broadcast("gradient", {"test": "message"})
        assert len(results) == 2  # to regulation and memory
        assert "regulation" in results
        assert "memory" in results

    def test_integrate_cycle(self):
        lattice = CrossRealmCoherenceLattice()
        result = lattice.integrate_cycle()
        assert "lattice_stability" in result
        assert "active_bridges" in result

    def test_lattice_status(self):
        lattice = CrossRealmCoherenceLattice()
        status = lattice.get_lattice_status()
        assert "lattice_stability" in status
        assert "active_bridges" in status
        assert "total_bridges" in status

    def test_reset(self):
        lattice = CrossRealmCoherenceLattice()
        lattice.integrate_cycle()
        # After reset, cycle goes back to 0
        lattice.reset()
        assert lattice.cycle == 0
        assert lattice.lattice_stability == 1.0
        # After reset: cycle=0, stability=1.0 (fresh lattice)


class TestCoherenceIntegrationHandler:
    def test_status(self):
        result = handler({"action": "status"})
        assert result["wave"] == 88

    def test_connect(self):
        result = handler({"action": "connect", "source": "gradient", "target": "regulation", "strength": 0.5})
        assert result["status"] == "bridge_activated"

    def test_broadcast(self):
        handler({"action": "broadcast", "source": "gradient", "message": {"test": "data"}})
        result = handler({"action": "lattice_status"})
        assert result["active_bridges"] >= 0

    def test_integrate(self):
        handler({"action": "integrate"})
        result = handler({"action": "lattice_status"})
        assert result["cycle"] >= 1

    def test_lattice_status(self):
        result = handler({"action": "lattice_status"})
        assert result["wave"] == 88

    def test_reset(self):
        result = handler({"action": "reset"})
        assert result["action"] == "reset"

    def test_unknown_action(self):
        result = handler({"action": "bogus"})
        assert "error" in result


def test_coherence_vitals_wave88():
    v = coherence_vitals()
    assert v["organ"] == "wave88_cross_realm_bridges"
    assert v["wave"] == 88
    assert v["status"] == "active"
