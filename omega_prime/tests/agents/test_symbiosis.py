import pytest
from omega_prime.agents.symbiosis import SymbiosisManager, BondState


class TestSymbiosisManager:
    def test_form_cross_species_bond(self):
        mgr = SymbiosisManager()
        bond = mgr.propose("s1", "sentinel", "w1", "wanderer")
        assert bond is not None
        assert bond.state == BondState.ACTIVE

    def test_same_species_refused(self):
        mgr = SymbiosisManager()
        bond = mgr.propose("a", "sentinel", "b", "sentinel")
        assert bond is None

    def test_agent_already_bonded(self):
        mgr = SymbiosisManager()
        mgr.propose("s1", "sentinel", "w1", "wanderer")
        bond2 = mgr.propose("s1", "sentinel", "a1", "architect")
        assert bond2 is None

    def test_get_partner(self):
        mgr = SymbiosisManager()
        mgr.propose("s1", "sentinel", "w1", "wanderer")
        assert mgr.get_partner("s1") == "w1"
        assert mgr.get_partner("w1") == "s1"

    def test_shared_capabilities_sentinel_wanderer(self):
        mgr = SymbiosisManager()
        mgr.propose("s1", "sentinel", "w1", "wanderer")
        caps = mgr.get_shared_capabilities("s1")
        assert "safe_exploration" in caps

    def test_tick_decays_and_dissolves(self):
        mgr = SymbiosisManager()
        mgr.propose("s1", "sentinel", "w1", "wanderer")
        dissolved = mgr.tick(decay_rate=1.0)
        assert len(dissolved) == 1
        assert mgr.get_partner("s1") is None

    def test_active_bonds_count(self):
        mgr = SymbiosisManager()
        mgr.propose("s1", "sentinel", "w1", "wanderer")
        mgr.propose("a1", "architect", "w2", "wanderer")
        assert len(mgr.active_bonds) == 2
