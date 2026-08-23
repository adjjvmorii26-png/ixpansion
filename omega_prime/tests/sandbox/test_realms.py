from omega_prime.sandbox.realms.lattice_realm import LatticeRealm
from omega_prime.sandbox.realms.void_realm import VoidRealm
from omega_prime.sandbox.realms.continuum_realm import ContinuumRealm


class TestLatticeRealm:
    def test_materialize(self):
        realm = LatticeRealm()
        realm.materialize({"size": 4})
        obs = realm.observation
        assert obs["size"] == 4

    def test_advance_counts_moves(self):
        realm = LatticeRealm()
        realm.materialize({})
        result = realm.advance([{"intent": "move"}, {"intent": "move"}, {"intent": "idle"}])
        assert result["moved"] == 2


class TestVoidRealm:
    def test_observation(self):
        realm = VoidRealm()
        realm.materialize({"entities": {"e1": {}}})
        assert "e1" in realm.observation["entities"]


class TestContinuumRealm:
    def test_physics_integration(self):
        realm = ContinuumRealm()
        realm.materialize({"bodies": {"b1": {"position": [0, 0], "velocity": [1, 0]}}})
        result = realm.advance([{"body_id": "b1"}])
        assert result["t"] == 1.0
