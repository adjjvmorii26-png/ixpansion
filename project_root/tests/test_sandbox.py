import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from nucleus.sandbox.world_state import WorldState
from nucleus.sandbox.event_mesh import EventMesh
from nucleus.sandbox.domains.physics import PhysicsDomain
from nucleus.sandbox.domains.economy import EconomyDomain
from nucleus.sandbox.domains.culture import CultureDomain
from nucleus.sandbox.domains.emergent_behavior import EmergentBehaviorDomain


class TestWorldState:
    def test_advance_tick(self):
        ws = WorldState()
        assert ws.tick == 0
        ws.advance()
        assert ws.tick == 1

    def test_entities(self):
        ws = WorldState()
        ws.place_entity("e1", {"type": "agent"})
        assert "e1" in ws.entity_ids
        assert ws.remove_entity("e1") is True


class TestEventMesh:
    def test_publish_and_subscribe(self):
        mesh = EventMesh()
        received = []
        mesh.subscribe("physical", lambda e: received.append(e))
        delivered = mesh.publish("physical", "collision", {"agents": ["a", "b"]})
        assert delivered >= 1
        assert len(received) >= 1

    def test_layer_propagation(self):
        mesh = EventMesh()
        meta_events = []
        mesh.subscribe("meta", lambda e: meta_events.append(e))
        # Publish at physical layer; should propagate up to meta
        mesh.publish("physical", "move", {"who": "a"})
        assert len(meta_events) >= 1


class TestPhysicsDomain:
    def test_gravity_integration(self):
        phys = PhysicsDomain()
        pos, vel = phys.integrate((0, 100), (5, 0), dt=1.0)
        assert vel[1] < 0  # Gravity pulled velocity down
        assert pos[0] > 0  # Moved forward

    def test_distance(self):
        phys = PhysicsDomain()
        assert phys.distance((0, 0), (3, 4)) == pytest.approx(5.0)


class TestEconomyDomain:
    def test_transfer(self):
        eco = EconomyDomain()
        eco.credit("a", 100)
        assert eco.transfer("a", "b", 50) is True
        assert eco._balances["a"] == 50
        assert eco._balances["b"] == 50

    def test_insufficient_funds(self):
        eco = EconomyDomain()
        eco.credit("poor", 10)
        assert eco.transfer("poor", "rich", 100) is False


class TestCultureDomain:
    def test_norm_lifecycle(self):
        culture = CultureDomain()
        culture.establish_norm("share_resources", 0.5)
        for _ in range(10):
            culture.reinforce_norm("share_resources", "agent_1")
        assert "share_resources" in culture.strong_norms

    def test_violation_penalty(self):
        culture = CultureDomain()
        culture.establish_norm("no_violence", 0.8)
        penalty = culture.violate_norm("no_violence", "aggressor")
        assert penalty > 0


class TestEmergentBehavior:
    def test_action_not_yet_codified(self):
        domain = EmergentBehaviorDomain(seed=42)
        result = domain.observe_action("agent_1", "teleport_without_crystal")
        assert result["codified"] is False

    def test_codification_at_threshold(self):
        domain = EmergentBehaviorDomain(seed=42)
        for i in range(8):
            domain.observe_action(f"agent_{i}", "phase_shift")
        assert domain.is_rule_active("phase_shift")
