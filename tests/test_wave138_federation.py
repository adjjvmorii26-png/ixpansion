"""Wave 138 — Sovereign Federation Layer tests."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))

from federation_treaty import FederationTreaty
from realm_ambassador import RealmAmbassador
from cross_realm_trade import CrossRealmTrade
from alliance_bank import AllianceBank
from border_diplomacy import BorderDiplomacy
from frontier_scout import FrontierScout
from immigrant_integration import ImmigrantIntegration
from summit_orchestrator import SummitOrchestrator


def test_wave138_federation_treaty():
    ft = FederationTreaty()
    treaty = ft.propose("reciprocal aid", "ixpansion", "omega realm", ["hex_lore", "physics"])
    assert not ft.ratify(treaty.id, trust_a=0.3, trust_b=0.5)  # below threshold
    assert ft.ratify(treaty.id, trust_a=0.9, trust_b=0.6)
    assert len(ft.active_treaties()) >= 1
    assert ft.status()["ratified"] >= 1


def test_wave138_realm_ambassador():
    ra = RealmAmbassador()
    amb = ra.post("aleph envoy", "omega realm")
    results = [ra.negotiate(amb.id, difficulty=0.1) for _ in range(3)]
    assert any(results)
    assert amb.success_rate() > 0
    assert ra.best_diplomat() == amb.id
    assert ra.status()["ambassadors"] >= 1


def test_wave138_cross_realm_trade():
    ct = CrossRealmTrade(lane_cost=0.05)
    good = ct.execute("ixpansion", "omega", "hex_lore", 100.0,
                      local_price=2.0, foreign_price=5.0)
    assert good["profitable"]
    bad = ct.execute("ixpansion", "omega", "sand", 100.0,
                     local_price=1.0, foreign_price=1.0)
    assert not bad["profitable"]
    assert ct.status()["cleared"] >= 1
    assert ct.status()["net_volume"] > 0


def test_wave138_alliance_bank():
    ab = AllianceBank(reserve_ratio=0.2)
    ab.deposit("ixpansion", 1000.0)
    ab.deposit("omega", 1000.0)
    assert ab.issue_credit("ixpansion", 100.0)  # within capacity
    assert not ab.issue_credit("ixpansion", 99999.0)  # exceeds
    ab.repay("ixpansion", 50.0)
    assert ab.stability_ratio() > 0
    assert ab.status()["realms"] >= 2


def test_wave138_border_diplomacy():
    bd = BorderDiplomacy(openness=0.5)
    assert bd.passage("scout", "omega", "ixpansion", risk_level=0.2)
    assert not bd.passage("raider", "omega", "ixpansion", risk_level=0.9)
    assert bd.border_tariff(100.0) == 5.0
    assert bd.risk_pressure() > 0
    assert bd.status()["crossings"] >= 2


def test_wave138_frontier_scout():
    fs = FrontierScout(engage_threshold=0.5)
    fs.scout("forest realm", opportunity=0.9, risk=0.1, compatibility=0.8)
    fs.scout("dead realm", opportunity=0.2, risk=0.9, compatibility=0.1)
    assert len(fs.prime_targets()) >= 1
    best = fs.status()["prime_targets"]
    assert best >= 1
    # engage the first prime target
    prime = fs.prime_targets()[0]
    assert fs.engage(prime["id"])
    assert fs.status()["engagements"] >= 1


def test_wave138_immigrant_integration():
    ii = ImmigrantIntegration()
    ii.register_mentor("senior weaver")
    immigrant = ii.receive("nova", "omega realm", skills_transferable=0.9, culture_fit=0.8)
    assert immigrant.mentor == "senior weaver"
    assert ii.integrate(immigrant.id)
    assert immigrant.status == "integrated"
    assert ii.status()["integrated"] >= 1


def test_wave138_summit_orchestrator():
    so = SummitOrchestrator(quorum=3)
    so.convene(["a", "b", "c", "d"])
    res = so.introduce("open trade lanes", "commerce")
    so.vote(res.id, "a", True)
    so.vote(res.id, "b", True)
    so.vote(res.id, "c", False)
    assert so.tally(res.id)
    assert res.votes_for >= 2
    assert so.status()["summits"] >= 1


def test_wave138_handlers():
    from federation_treaty import handler as h1
    from realm_ambassador import handler as h2
    from cross_realm_trade import handler as h3
    from alliance_bank import handler as h4
    from border_diplomacy import handler as h5
    from frontier_scout import handler as h6
    from immigrant_integration import handler as h7
    from summit_orchestrator import handler as h8
    for h in (h1, h2, h3, h4, h5, h6, h7, h8):
        r = h({})
        assert r["status"] == "active"
