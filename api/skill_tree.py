"""Skill Tree — hierarchical capability structures that agents unlock progressively.

Agents unlock skills in a tree structure: basic skills unlock advanced ones.
Skills can be taught to other agents, creating a knowledge transfer economy.
The tree reveals which capabilities are prerequisites for advanced work.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class Skill:
    def __init__(self, name: str, tier: int = 0, prerequisites: List[str] = None):
        self.name = name
        self.tier = tier
        self.prerequisites = prerequisites or []
        self.mastery: Dict[str, float] = {}

    def can_learn(self, unlocked: Set[str]) -> bool:
        return all(p in unlocked for p in self.prerequisites)

    def teach(self, teacher: str, learner: str) -> Dict[str, Any]:
        teacher_mastery = self.mastery.get(teacher, 0)
        transfer = teacher_mastery * random.uniform(0.3, 0.6)
        self.mastery[learner] = min(1.0, self.mastery.get(learner, 0) + transfer)
        self.mastery[teacher] = min(1.0, teacher_mastery + 0.05)
        return {"skill": self.name, "teacher": teacher, "learner": learner, "transferred": round(transfer, 3)}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "tier": self.tier,
            "prerequisites": self.prerequisites,
            "agents": len(self.mastery),
            "avg_mastery": round(
                sum(self.mastery.values()) / max(len(self.mastery), 1), 3
            ),
        }


class SkillTree:
    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self.agent_unlocks: Dict[str, Set[str]] = {}
        self.teaching_log: List[Dict[str, Any]] = []

    def define_skill(self, name: str, tier: int = 0, prerequisites: List[str] = None) -> Dict[str, Any]:
        skill = Skill(name, tier, prerequisites)
        self.skills[name] = skill
        return {"defined": skill.to_dict()}

    def unlock(self, agent_id: str, skill_name: str) -> Dict[str, Any]:
        if skill_name not in self.skills:
            return {"error": "skill not found"}
        self.agent_unlocks.setdefault(agent_id, set())
        skill = self.skills[skill_name]
        if not skill.can_learn(self.agent_unlocks[agent_id]):
            missing = [p for p in skill.prerequisites if p not in self.agent_unlocks[agent_id]]
            return {"error": "prerequisites not met", "missing": missing}
        self.agent_unlocks[agent_id].add(skill_name)
        skill.mastery[agent_id] = 0.1
        return {"unlocked": skill_name, "agent": agent_id, "tier": skill.tier}

    def teach(self, teacher: str, learner: str, skill_name: str) -> Dict[str, Any]:
        if skill_name not in self.skills:
            return {"error": "skill not found"}
        if teacher not in self.skills[skill_name].mastery:
            return {"error": "teacher doesn't know this skill"}
        result = self.skills[skill_name].teach(teacher, learner)
        self.agent_unlocks.setdefault(learner, set())
        self.agent_unlocks[learner].add(skill_name)
        self.teaching_log.append({**result, "time": time.time()})
        return result

    def agent_skills(self, agent_id: str) -> Dict[str, Any]:
        unlocked = self.agent_unlocks.get(agent_id, set())
        skills = []
        for name in unlocked:
            if name in self.skills:
                skill = self.skills[name]
                skills.append({
                    "name": name,
                    "tier": skill.tier,
                    "mastery": round(skill.mastery.get(agent_id, 0), 3),
                })
        return {"agent": agent_id, "skills": sorted(skills, key=lambda x: x["tier"])}

    def tree_overview(self) -> List[Dict[str, Any]]:
        return sorted(
            [s.to_dict() for s in self.skills.values()],
            key=lambda x: x["tier"],
        )

    def tree_stats(self) -> Dict[str, Any]:
        tier_counts: Dict[int, int] = {}
        for s in self.skills.values():
            tier_counts[s.tier] = tier_counts.get(s.tier, 0) + 1
        return {
            "total_skills": len(self.skills),
            "total_unlocks": sum(len(u) for u in self.agent_unlocks.values()),
            "total_teachings": len(self.teaching_log),
            "tier_distribution": tier_counts,
        }


_tree = SkillTree()


def skill_tree_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "define":
        return _tree.define_skill(
            payload.get("name", f"skill_{random.randint(100,999)}"),
            payload.get("tier", 0),
            payload.get("prerequisites"),
        )
    elif action == "unlock":
        return _tree.unlock(payload.get("agent_id", "learner"), payload.get("skill_name", ""))
    elif action == "teach":
        return _tree.teach(
            payload.get("teacher", ""), payload.get("learner", ""),
            payload.get("skill_name", ""),
        )
    elif action == "agent_skills":
        return _tree.agent_skills(payload.get("agent_id", ""))
    elif action == "overview":
        return {"skills": _tree.tree_overview()}
    return {"status": "active", **_tree.tree_stats()}


handler = skill_tree_handler
