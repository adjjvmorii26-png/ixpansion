"""Wave 137 — Adaptation & Resilience Layer tests."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))

from resilience_engine import ResilienceEngine
from stress_simulator import StressSimulator
from recovery_protocol import RecoveryProtocol
from adaptation_learner import AdaptationLearner
from failure_injection import FailureInjection
from hazard_warning import HazardWarning
from continuity_planner import ContinuityPlanner
from antifragility_core import AntifragilityCore


def test_wave137_resilience_engine():
    re = ResilienceEngine()
    re.add("ledger", redundancy=1, load=0.9)
    re.add("router", redundancy=3, load=0.3)
    assert re.overall_resilience() < 1.0
    assert "ledger" in re.spofs()
    ledger = [s for s in re._subsystems.values() if s.name == "ledger"][0]
    assert re.harden(ledger.id)
    assert "ledger" not in re.spofs()


def test_wave137_stress_simulator():
    ss = StressSimulator()
    s1 = ss.scenario("spike_load", severity=0.8)
    s2 = ss.scenario("economic_crash", severity=0.9)
    r1 = ss.execute(s1.id, baseline_resilience=0.9)
    r2 = ss.execute(s2.id, baseline_resilience=0.9)
    assert r1 < 0.9 and r2 < 0.9
    assert r2 < r1  # crash is more severe
    assert ss.status()["runs"] >= 2
    assert ss.weakest() == s2.id


def test_wave137_recovery_protocol():
    rp = RecoveryProtocol()
    plan = rp.plan("ledger recovery", [
        {"name": "snapshot", "action": "restore from backup", "rollback": "keep current"},
        {"name": "verify", "action": "run integrity check", "rollback": "report"},
    ])
    assert rp.execute(plan.id)
    assert plan.status == "complete"
    assert rp.status()["completed"] >= 1


def test_wave137_adaptation_learner():
    al = AdaptationLearner()
    l1 = al.record("spike_load", "router saturated", "add redundancy")
    al.record("spike_load", "queue backlogs", "add backpressure")
    assert al.apply(l1.id, effectiveness=0.85)
    assert al.emerging_patterns() == ["spike_load"]
    assert al.status()["adaptations_applied"] >= 1


def test_wave137_failure_injection():
    fi = FailureInjection(auto_contain=True)
    fi.inject("state_core", "partial write", severity=0.4)
    fi.inject("ledger", "recovery drill", severity=0.2)
    assert fi.blast_radius() == 0
    assert fi.recovery_triggered()
    assert fi.status()["contained"] >= 2


def test_wave137_hazard_warning():
    hw = HazardWarning()
    sev = hw.evaluate("router", "load", 0.95, {"caution": 0.6, "warning": 0.75, "critical": 0.9})
    assert sev == "critical"
    sev2 = hw.evaluate("ledger", "drift", 0.5, {"watch": 0.9, "caution": 0.95, "warning": 0.98, "critical": 1.0})
    assert sev2 == "info"
    assert len(hw.active_hazards()) >= 1
    assert hw.status()["notified_actions"] >= 1


def test_wave137_continuity_planner():
    cp = ContinuityPlanner(rto_target=60.0, rpo_target=15.0)
    cp.add_backup("s3_mirror")
    cp.add_backup("local_snapshot")
    cp.set_resume_order(["state_core", "ledger", "router"])
    result = cp.record_recovery(rto_s=45.0, rpo_s=10.0)
    assert result == {"rto_met": True, "rpo_met": True}
    assert cp.ready()
    assert cp.status()["backups"] >= 2


def test_wave137_antifragility_core():
    ac = AntifragilityCore(base_capacity=100.0)
    dividend = ac.survive_shock(severity=0.8, recovery_quality=0.9)
    assert dividend > 0
    assert ac.capacity() > 100.0
    assert ac.fragility_gain() > 0
    assert ac.status()["shocks_survived"] >= 1


def test_wave137_handlers():
    from resilience_engine import handler as h1
    from stress_simulator import handler as h2
    from recovery_protocol import handler as h3
    from adaptation_learner import handler as h4
    from failure_injection import handler as h5
    from hazard_warning import handler as h6
    from continuity_planner import handler as h7
    from antifragility_core import handler as h8
    for h in (h1, h2, h3, h4, h5, h6, h7, h8):
        r = h({})
        assert r["status"] == "active"
