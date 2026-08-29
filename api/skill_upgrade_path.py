"""Wave 131 — Skill Upgrade Path.

Workers evolve by learning new skills over time. Each task completed in
a skill domain increases proficiency; workers can unlock advanced
capabilities when proficiency thresholds are met.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List


class Skill:
    """A skill with a proficiency level."""

    LEVELS = ["novice", "apprentice", "competent", "proficient", "expert", "master"]

    def __init__(self, name: str, proficiency: float = 0.0):
        self.name = name
        self.proficiency = proficiency
        self.practice_count = 0
        self.created = time.time()

    def practice(self, experience: float = 0.1) -> float:
        self.proficiency = min(1.0, self.proficiency + experience)
        self.practice_count += 1
        return self.proficiency

    @property
    def level(self) -> str:
        idx = min(int(self.proficiency * len(self.LEVELS)), len(self.LEVELS) - 1)
        return self.LEVELS[idx]

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "proficiency": round(self.proficiency, 4),
                "level": self.level, "practice_count": self.practice_count}


class SkillUpgradePath:
    """Manages skill evolution for workers."""

    def __init__(self):
        self._skills: Dict[str, Skill] = {}
        self._masteries: List[str] = []

    def add_skill(self, name: str, initial: float = 0.0) -> Skill:
        skill = Skill(name, initial)
        self._skills[name] = skill
        return skill

    def practice(self, skill_name: str, experience: float = 0.1) -> Dict[str, Any]:
        skill = self._skills.get(skill_name)
        if not skill:
            return {"error": f"skill '{skill_name}' not found"}
        level_before = skill.level
        proficiency = skill.practice(experience)
        result = {"skill": skill_name, "proficiency": round(proficiency, 4),
                  "level": skill.level}
        if skill.level != level_before:
            result["leveled_up"] = level_before
            self._masteries.append(f"{skill_name}:{skill.level}")
        return result

    def skilled_agents(self, skill_name: str, min_level: str = "competent") -> List[Dict[str, Any]]:
        skill = self._skills.get(skill_name)
        if not skill:
            return []
        levels = Skill.LEVELS
        min_idx = levels.index(min_level)
        if levels.index(skill.level) >= min_idx:
            return [skill.to_dict()]
        return []

    def status(self) -> Dict[str, Any]:
        return {"total_skills": len(self._skills), "masteries": len(self._masteries)}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    return {"status": "active", "module": "skill_upgrade_path"}
