"""Wave 134 — Autonomous Ascension Layer tests."""
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))

from autonomous_contracts import AutonomousContracts
from workforce_nexus import WorkforceNexus
from conflict_arbitrator import ConflictArbitrator
from succession_planner import SuccessionPlanner
from worker_wellness import WorkerWellness
from guild_orders import GuildOrders
from autonomy_dial import AutonomyDial, LEVELS
from self_improvement_loop import SelfImprovementLoop


def test_wave134_autonomous_contracts():
    ac = AutonomousContracts()
    c = ac.create("guild expansion", "alice", "guildmaster", payment=100.0)
    assert ac.sign(c.id)
    amt = ac.deliver(c.id, on=time.time())  # on time
    assert amt == 100.0
    assert ac.status()["settled"] >= 1
    assert ac.status()["settled_value"] >= 100.0


def test_wave134_workforce_nexus():
    wn = WorkforceNexus()
    wn.register_unit("alice", "scout")
    wn.register_unit("bob", "architect")
    wn.pulse(0.9, 0.8, 0.7, 0.8)
    wn.pulse(0.6, 0.5, 0.6, 0.5)
    assert wn.trend() < 0
    assert len(wn.org_chart()) >= 2
    assert "alice" in wn.power_balance()


def test_wave134_conflict_arbitrator():
    ca = ConflictArbitrator()
    d = ca.file("alice", "bob", "territory")
    ruling = ca.arbitrate(d.id, rep_claimant=0.9, rep_respondent=0.3)
    assert ruling == "claimant"
    # second dispute on same subject uses precedent
    d2 = ca.file("bob", "alice", "territory")
    ruling2 = ca.arbitrate(d2.id, rep_claimant=0.3, rep_respondent=0.9)
    assert ruling2 == "claimant"  # precedent wins over reputation
    assert ca.status()["precedents"] >= 1


def test_wave134_succession_planner():
    sp = SuccessionPlanner()
    line = sp.designate("overseer", ["bob", "carol"])
    assert line.gap_covered
    promoted = sp.emergency_promote("overseer")
    assert promoted == "bob"
    assert sp.status()["promotions"] >= 1
    assert "overseer" not in sp.coverage_gaps()  # carol still covers


def test_wave134_worker_wellness():
    ww = WorkerWellness()
    ww.register("alice")
    ww.work("alice", 0.3)
    ww.work("alice", 0.3)
    ww.work("alice", 0.3)
    assert ww._wellness["alice"] < 1.0
    ww.rest("alice", 0.4)
    assert ww.status()["alerts"] >= 0
    assert ww.status()["workers"] >= 1
    assert ww.status()["avg_wellness"] > 0


def test_wave134_guild_orders():
    go = GuildOrders()
    go.register_guild("hex guild", "hex")
    o = go.commission("client1", "build dialect", "hex", 50.0)
    assert go.route(o.id, bid=60.0)
    assert go.complete(o.id, rating=0.95)
    assert go.status()["fulfilled"] >= 1
    assert go.status()["revenue"] >= 60.0


def test_wave134_autonomy_dial():
    ad = AutonomyDial(level=1)
    assert ad.current() in LEVELS
    assert not ad.may_act_alone("delete_data")  # supervised
    ad.set_level(4)
    assert ad.current() == "self_directing"
    assert ad.may_act_alone("new_module")
    assert not ad.may_act_alone("rewrite_core")  # safety rail
    assert ad.summary()["level"] == 4


def test_wave134_self_improvement_loop():
    sil = SelfImprovementLoop(risk_threshold=0.45)
    p = sil.propose("alice", "auto-hex", impact=0.9, risk=0.1)
    assert p.status == "installed"
    p2 = sil.propose("bob", "core rewrite", impact=0.8, risk=0.9)
    assert p2.status == "review"
    assert sil.approve(p2.id)
    assert sil.status()["installed"] >= 2
    assert sil.status()["review_queue"] == 0


def test_wave134_handlers():
    from autonomous_contracts import handler as h1
    from workforce_nexus import handler as h2
    from conflict_arbitrator import handler as h3
    from succession_planner import handler as h4
    from worker_wellness import handler as h5
    from guild_orders import handler as h6
    from autonomy_dial import handler as h7
    from self_improvement_loop import handler as h8
    for h in (h1, h2, h3, h4, h5, h6, h7, h8):
        r = h({})
        assert r["status"] == "active"
