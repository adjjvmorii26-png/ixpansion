"""Wave 131 — Autonomous Workforce Layer tests."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))

from workforce_orchestrator import WorkforceOrchestrator
from skill_upgrade_path import SkillUpgradePath, Skill
from task_mesh import TaskMesh
from collaboration_hub import CollaborationHub
from performance_reviewer import PerformanceReviewer
from automation_director import AutomationDirector
import time
from team_formation import TeamFormation
from worker_economy import WorkerEconomy


def test_wave131_workforce_orchestrator():
    orch = WorkforceOrchestrator()
    orch.hire("alpha", ["coding", "testing"])
    orch.hire("beta", ["analysis"])
    task = orch.create_task("build module", ["coding"], priority=2)
    assigned = orch.schedule()
    assert assigned >= 1
    assert orch.complete_task(task.id, quality=0.9)
    stats = orch.workforce_stats()
    assert stats["workers"] >= 2
    assert stats["total_completed"] >= 1


def test_wave131_skill_upgrade_path():
    path = SkillUpgradePath()
    skill = path.add_skill("hex", initial=0.0)
    path.practice("hex", 0.6)
    assert skill.proficiency > 0.5
    assert skill.level in Skill.LEVELS
    assert path.status()["total_skills"] >= 1


def test_wave131_task_mesh():
    mesh = TaskMesh()
    root = mesh.add_task("root task")
    child = mesh.add_task("child task", parent_id=root.id)
    assert child.parent_id == root.id
    mesh.add_worker("w1")
    mesh.add_worker("w2")
    assert mesh.assign_all() >= 2
    assert mesh.complete(root.id)
    stats = mesh.status()
    assert stats["total_tasks"] >= 2
    assert stats["completed"] >= 1


def test_wave131_collaboration_hub():
    hub = CollaborationHub()
    task = hub.create_group_task("ship feature", ["a", "b"], chunks=2)
    key = task.id
    assert hub.progress_group_task(key)
    hub.post_message("a", "ready", "build")
    assert len(hub.messages()) >= 1
    assert hub.status()["group_tasks"] >= 1


def test_wave131_performance_reviewer():
    rev = PerformanceReviewer()
    rev.register("alice")
    rev.review("alice", 0.9, 0.9)
    rev.review("alice", 0.8, 0.8)
    assert rev.tier("alice") in PerformanceReviewer.TIERS
    assert rev.report("alice")["reviews"] >= 2
    assert rev.promote("alice")
    assert rev.status()["promotions"] >= 1


def test_wave131_automation_director():
    director = AutomationDirector()
    j1 = director.register("nightly cleanup", 5)
    director.register("rebalance", 10)
    jobs = director.tick(now=time.time() + 100.0, duration_s=0.5)
    assert jobs >= 1
    assert director.pause(j1.id)
    assert director.resume(j1.id, now=200.0)
    assert director.status()["jobs"] >= 2


def test_wave131_team_formation():
    form = TeamFormation()
    form.add_worker("a", ["alpha", "beta"])
    form.add_worker("b", ["beta", "gamma"])
    form.add_worker("c", ["delta"])
    combo = form.strongest_combination(["a", "b", "c"], 2)
    assert combo  # non-empty
    team = form.form("core", combo, mission="seed")
    assert team is not None
    assert team.coverage() >= 2
    assert form.status()["teams"] >= 1


def test_wave131_worker_economy():
    econ = WorkerEconomy()
    econ.enroll("alice")
    econ.enroll("bob")
    assert econ.pay("alice", 50.0)
    assert econ.transfer("alice", "bob", 20.0)
    assert econ.balance("alice") > 120.0
    assert econ.balance("bob") > 110.0
    econ.set_item_price("blueprint", 15.0)
    assert econ.status()["wallets"] >= 2


def test_wave131_handlers():
    from workforce_orchestrator import handler as h_wo
    from collaboration_hub import handler as h_ch
    from performance_reviewer import handler as h_pr
    from automation_director import handler as h_ad
    from team_formation import handler as h_tf
    from worker_economy import handler as h_we
    for h in (h_wo, h_ch, h_pr, h_ad, h_tf, h_we):
        r = h({})
        assert r["status"] == "active"
