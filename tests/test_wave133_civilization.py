"""Wave 133 — Workforce Civilization Layer tests."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))

from civilization_kernel import CivilizationKernel
from heritage_system import HeritageSystem
from worker_council import WorkerCouncil
from innovation_lab import InnovationLab
from craft_guilds import CraftGuilds
from civilization_timeline import CivilizationTimeline
from diaspora_engine import DiasporaEngine
from values_compass import ValuesCompass


def test_wave133_civilization_kernel():
    ck = CivilizationKernel()
    ck.set_policy("max_utilization", 0.8)
    ck.observe(0.9, 0.8, 0.9)
    ck.observe(0.5, 0.4, 0.5)
    assert ck.drift() < 0
    assert ck.intervention_needed(threshold=0.2)
    assert ck.status()["health_samples"] >= 2


def test_wave133_heritage_system():
    hs = HeritageSystem()
    hs.initiate("alice")
    hs.teach("alice", "hex discipline")
    hs.initiate("bob", ancestor="alice")
    hs.teach("alice", "patience")
    assert hs.lineage("bob")[0] == "bob"
    assert len(hs.lineage("bob")) >= 2
    assert hs.status()["workers"] >= 2
    assert hs.status()["transfers"] >= 2


def test_wave133_worker_council():
    wc = WorkerCouncil()
    p = wc.submit("expand guilds", "alice", "let there be more craft")
    wc.set_reputation("alice", 0.9)
    wc.set_reputation("bob", 0.4)
    wc.vote(p.id, "alice", True)
    wc.vote(p.id, "bob", False)
    assert wc.tally(p.id) == "passed"
    assert wc.status()["passed"] >= 1


def test_wave133_innovation_lab():
    il = InnovationLab()
    i = il.submit("fractal reactor", "alice", novelty=0.9)
    assert il.launch(i.id)
    assert il.promote(i.id)
    i2 = il.submit("rusty widget", "bob", novelty=0.2)
    assert il.launch(i2.id)
    assert il.archive(i2.id)
    assert il.status()["promoted"] >= 1
    assert il.status()["archived"] >= 1


def test_wave133_craft_guilds():
    cg = CraftGuilds()
    g = cg.found("hexwork", standards=0.7)
    g.join("alice")
    assert not cg.certify("hexwork", "alice", reputation=0.5)  # below standards
    assert cg.certify("hexwork", "alice", reputation=0.9)
    assigned = cg.assign_work("hexwork", required_standards=0.6)
    assert assigned is not None
    assert cg.status()["guilds"] >= 1


def test_wave133_civilization_timeline():
    ct = CivilizationTimeline()
    ct.mark("Founding", "origin", "the workforce civilizes")
    ct.mark("Golden Age", "flourish", "guilds prosper")
    ct.mark("Crisis", "crisis", "entropy spike")
    assert ct.current_era() == "Crisis"
    assert len(ct.by_kind("crisis")) >= 1
    assert ct.status()["epochs"] >= 3


def test_wave133_diaspora_engine():
    de = DiasporaEngine()
    colony = de.splinter("hex colony", "origin", ["a", "b"])
    assert de.discover(colony.id, "new grammer")
    assert de.discover(colony.id, "cold fusion of modules")
    findings = de.reintegrate(colony.id)
    assert len(findings) >= 2
    assert de.status()["reintegrated"] >= 1


def test_wave133_values_compass():
    vc = ValuesCompass()
    vc.declare({"solidarity": 0.9, "curiosity": 0.4})
    assert vc.arbitrate("collective", "solo", "solidarity") == "collective"
    vc.record_decision(True)
    vc.record_decision(False)
    assert vc.status()["decisions"] >= 2
    assert vc.adjust("adaptation", 0.2) > 0.5


def test_wave133_handlers():
    from civilization_kernel import handler as h1
    from heritage_system import handler as h2
    from worker_council import handler as h3
    from innovation_lab import handler as h4
    from craft_guilds import handler as h5
    from civilization_timeline import handler as h6
    from diaspora_engine import handler as h7
    from values_compass import handler as h8
    for h in (h1, h2, h3, h4, h5, h6, h7, h8):
        r = h({})
        assert r["status"] == "active"
