"""Wave 132 — Labor Ecosystem Layer tests."""
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))

from workforce_genetics import WorkforceGenetics, TRAITS, Genome
from worker_narrative import WorkerNarrative
from labor_market import LaborMarket
from reputation_system import ReputationSystem, TRUST_TIERS
from autonomous_marketplace import AutonomousMarketplace
from career_ladder import CareerLadder, LADDER
from workforce_roster import WorkforceRoster
from attention_reservoir import AttentionReservoir


def test_wave132_workforce_genetics():
    g = WorkforceGenetics(seed=42)
    g.spawn("parent_a", {"curiosity": 0.9, "diligence": 0.7, "risk_tolerance": 0.5,
                         "collaboration": 0.6, "entropy_affinity": 0.4})
    g.spawn("parent_b", {"curiosity": 0.3, "diligence": 0.4, "risk_tolerance": 0.8,
                         "collaboration": 0.9, "entropy_affinity": 0.2})
    child = g.breed("child", "parent_a", "parent_b", generation=1, mutation_rate=0.1)
    assert isinstance(child, Genome)
    assert len(g.best_parents(top=2)) >= 1
    assert g.status()["workers"] >= 3


def test_wave132_worker_narrative():
    n = WorkerNarrative()
    n.add("alice", "First Task", "built a module", "proud")
    n.add("alice", "Failure", "learned a lesson", "humbled")
    n.add("bob", "Launch", "shipped artifact", "proud")
    assert len(n.story("alice")) >= 2
    assert n.shared_mood("alice", "bob") >= 1
    assert "alice" in n.workers()


def test_wave132_labor_market():
    m = LaborMarket()
    lot = m.list_labor("alice", "hex", 5.0)
    assert not m.bid(lot.id, "buyer1", 4.0)  # below asking
    assert m.bid(lot.id, "buyer1", 6.0)
    assert m.average_price() >= 6.0
    assert m.status()["settled"] >= 1


def test_wave132_reputation_system():
    r = ReputationSystem()
    r.register("alice")
    r.reward("alice", 0.6)
    r.reward("alice", 0.2)
    assert r.tier("alice") in TRUST_TIERS
    assert r.can_trust("alice", "trusted")
    r.penalize("alice", 0.5)
    assert r.status()["workers"] >= 1


def test_wave132_autonomous_marketplace():
    am = AutonomousMarketplace()
    p = am.list_product("agent v1", "alice", 10.0, reputation=0.5)
    assert p.price() >= 10.0
    assert am.buy(p.id, "customer1")
    assert not am.buy(p.id, "customer2")  # already sold
    assert am.status()["sales"] >= 1
    assert am.status()["revenue"] > 0


def test_wave132_career_ladder():
    c = CareerLadder()
    c.register("alice")
    promoted = None
    for _ in range(10):
        title = c.record_task("alice", reputation=0.6)
        if title:
            promoted = title
    assert c.rung("alice") in [r[0] for r in LADDER]
    assert c.wage("alice") >= LADDER[0][3]
    assert c.status()["workers"] >= 1


def test_wave132_workforce_roster():
    r = WorkforceRoster()
    shift = r.add_shift("day", 6, min_workers=1)
    assert r.assign("alice", shift.id)
    assert not r.assign("alice", shift.id)  # already assigned
    assert r.status()["shifts"] >= 1
    assert shift.covered()


def test_wave132_attention_reservoir():
    res = AttentionReservoir(capacity=100.0)
    assert res.request("alice", 10.0)
    assert res.request("bob", 20.0)
    assert not res.request("carol", 1000.0)  # exceeds capacity
    res.release("alice", 5.0)
    res.recharge(2.0)
    assert res.status()["allocated"] > 0
    assert res.status()["available"] < 100.0


def test_wave132_handlers():
    from workforce_genetics import handler as h1
    from worker_narrative import handler as h2
    from labor_market import handler as h3
    from reputation_system import handler as h4
    from autonomous_marketplace import handler as h5
    from career_ladder import handler as h6
    from workforce_roster import handler as h7
    from attention_reservoir import handler as h8
    for h in (h1, h2, h3, h4, h5, h6, h7, h8):
        r = h({})
        assert r["status"] == "active"
