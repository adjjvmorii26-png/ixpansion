"""Wave 126 — Hero Journey Mapper.

Maps system events onto the monomyth structure — ordinary world,
call to adventure, trials, ordeal, reward, return. Every significant
change follows the hero's journey.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List


class HeroJourney:
    """A hero's journey mapped from system events."""

    STAGES = ["ordinary_world", "call_to_adventure", "refusal", "mentor",
              "crossing_threshold", "trials", "ordeal", "reward",
              "road_back", "resurrection", "return"]

    def __init__(self, hero_name: str):
        self.hero_name = hero_name
        self.current_stage = 0
        self.stage_log: List[Dict[str, Any]] = []
        self.created = time.time()

    def advance(self, event: str = "") -> str:
        if self.current_stage < len(self.STAGES) - 1:
            self.current_stage += 1
        stage_name = self.STAGES[self.current_stage]
        self.stage_log.append({"stage": stage_name, "event": event, "timestamp": time.time()})
        return stage_name

    def current(self) -> str:
        return self.STAGES[self.current_stage]

    def is_complete(self) -> bool:
        return self.current_stage >= len(self.STAGES) - 1

    def to_dict(self) -> Dict[str, Any]:
        return {"hero": self.hero_name, "current_stage": self.current(),
                "completed": self.is_complete(), "progress": self.current_stage / max(len(self.STAGES) - 1, 1)}


class HeroJourneyMapper:
    """Maps system events onto hero's journey structure."""

    def __init__(self):
        self._journeys: List[HeroJourney] = []

    def begin_journey(self, hero_name: str) -> HeroJourney:
        journey = HeroJourney(hero_name)
        self._journeys.append(journey)
        return journey

    def advance_journey(self, hero_name: str, event: str = "") -> Dict[str, Any]:
        for j in self._journeys:
            if j.hero_name == hero_name:
                stage = j.advance(event)
                return {"hero": hero_name, "stage": stage, "complete": j.is_complete()}
        return {"error": f"Hero '{hero_name}' not found"}

    def status(self) -> Dict[str, Any]:
        completed = sum(1 for j in self._journeys if j.is_complete())
        return {"total_journeys": len(self._journeys), "completed": completed}
