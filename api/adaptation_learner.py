"""Wave 137 — Adaptation Learner.

Turns shocks into strategy. Every stress event and recovery is logged
as a lesson; the learner identifies recurring patterns and proposes
adaptations (policy changes, new redundancies, cultural shifts) that
make the civilization stronger for the next shock.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List


class Lesson:
    """A recorded adaptation insight from a past shock."""

    def __init__(self, shock: str, observation: str, adaptation: str):
        self.shock = shock
        self.observation = observation
        self.adaptation = adaptation
        self.applied = False
        self.effectiveness: float = 0.0
        self.created = time.time()
        self.id = hashlib.sha256(f"lesson:{shock}:{observation}".encode()).hexdigest()[:10]

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "shock": self.shock, "observation": self.observation,
                "adaptation": self.adaptation, "applied": self.applied,
                "effectiveness": self.effectiveness}


class AdaptationLearner:
    """Mines shock history into applied adaptations."""

    def __init__(self):
        self._lessons: Dict[str, Lesson] = {}
        self._adaptations_applied = 0

    def record(self, shock: str, observation: str, adaptation: str) -> Lesson:
        lesson = Lesson(shock, observation, adaptation)
        self._lessons[lesson.id] = lesson
        return lesson

    def apply(self, lesson_id: str, effectiveness: float = 0.8) -> bool:
        lesson = self._lessons.get(lesson_id)
        if lesson is None or lesson.applied:
            return False
        lesson.applied = True
        lesson.effectiveness = max(0.0, min(1.0, effectiveness))
        self._adaptations_applied += 1
        return True

    def emerging_patterns(self) -> List[str]:
        shocks = {}
        for lesson in self._lessons.values():
            shocks[lesson.shock] = shocks.get(lesson.shock, 0) + 1
        return [s for s, c in shocks.items() if c >= 2]

    def status(self) -> Dict[str, Any]:
        return {"lessons": len(self._lessons),
                "adaptations_applied": self._adaptations_applied,
                "recurring_patterns": self.emerging_patterns()}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    learner = AdaptationLearner()
    return {"status": "active", "module": "adaptation_learner",
            **learner.status()}

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "protocol", "status": "active", "wave": "137", "module": "adaptation_learner"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
