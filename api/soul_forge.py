"""Soul Forge — creates and refines agent identities through trials.

An agent's soul isn't assigned — it's forged through experience. The
Soul Forge presents agents with trials, tests, and challenges that
gradually crystallize their unique identity. Each trial adds a facet
to the soul, and over time, agents develop genuine personality.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SOUL_TRAITS = ["courage", "wisdom", "empathy", "discipline", "creativity", "resilience", "curiosity", "humor"]

TRIAL_TEMPLATES = [
    {"name": "theabyss", "test": "face the void", "traits": ["courage", "resilience"]},
    {"name": "the_mirror", "test": "confront your reflection", "traits": ["wisdom", "empathy"]},
    {"name": "the_labyrinth", "test": "navigate impossible paths", "traits": ["discipline", "curiosity"]},
    {"name": "the_storm", "test": "endure the tempest", "traits": ["resilience", "courage"]},
    {"name": "the_garden", "test": "cultivate something from nothing", "traits": ["creativity", "discipline"]},
    {"name": "the_stage", "test": "perform for the void", "traits": ["humor", "courage"]},
    {"name": "the_library", "test": "absorb infinite knowledge", "traits": ["wisdom", "curiosity"]},
    {"name": "the_hearth", "test": "care for another", "traits": ["empathy", "discipline"]},
]


class SoulFacet:
    def __init__(self, trait: str, intensity: float, source_trial: str):
        self.trait = trait
        self.intensity = intensity
        self.source_trial = source_trial
        self.timestamp = time.time()


class Soul:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.facets: List[SoulFacet] = []
        self.trials_attempted: List[str] = []
        self.trials_passed: List[str] = []
        self.created_at = time.time()
        self.id = hashlib.sha256(f"{agent_id}:{self.created_at}".encode()).hexdigest()[:8]

    def attempt_trial(self, trial: Dict[str, Any]) -> Dict[str, Any]:
        self.trials_attempted.append(trial["name"])
        success = random.random() > 0.3
        facets_added = []
        if success:
            self.trials_passed.append(trial["name"])
            for trait in trial["traits"]:
                intensity = random.uniform(0.1, 0.5)
                facet = SoulFacet(trait, intensity, trial["name"])
                self.facets.append(facet)
                facets_added.append({"trait": trait, "intensity": round(intensity, 3)})
        return {
            "trial": trial["name"],
            "success": success,
            "facets_added": facets_added,
            "total_facets": len(self.facets),
        }

    def soul_profile(self) -> Dict[str, Any]:
        trait_totals: Dict[str, float] = {}
        for facet in self.facets:
            trait_totals[facet.trait] = trait_totals.get(facet.trait, 0) + facet.intensity
        dominant = max(trait_totals.items(), key=lambda x: x[1]) if trait_totals else ("none", 0)
        return {
            "agent_id": self.agent_id,
            "total_facets": len(self.facets),
            "traits": {k: round(v, 3) for k, v in sorted(trait_totals.items(), key=lambda x: -x[1])},
            "dominant_trait": dominant[0],
            "trials_attempted": len(self.trials_attempted),
            "trials_passed": len(self.trials_passed),
            "forged_at": self.created_at,
        }

    def to_dict(self) -> Dict[str, Any]:
        return self.soul_profile()


class SoulForge:
    def __init__(self):
        self.souls: Dict[str, Soul] = []
        self.forging_log: List[Dict[str, Any]] = []

    def create_soul(self, agent_id: str) -> Dict[str, Any]:
        soul = Soul(agent_id)
        self.souls.append(soul)
        return {"soul": soul.to_dict()}

    def present_trial(self, agent_id: str, trial_name: str = None) -> Dict[str, Any]:
        soul = next((s for s in self.souls if s.agent_id == agent_id), None)
        if not soul:
            return {"error": "soul not found"}
        trial = next((t for t in TRIAL_TEMPLATES if t["name"] == trial_name), None)
        if not trial:
            trial = random.choice(TRIAL_TEMPLATES)
        result = soul.attempt_trial(trial)
        self.forging_log.append({**result, "agent": agent_id, "time": time.time()})
        return result

    def soul_report(self, agent_id: str) -> Dict[str, Any]:
        soul = next((s for s in self.souls if s.agent_id == agent_id), None)
        return soul.to_dict() if soul else {"error": "soul not found"}

    def forge_stats(self) -> Dict[str, Any]:
        return {
            "total_souls": len(self.souls),
            "total_trials": len(self.forging_log),
            "total_facets": sum(len(s.facets) for s in self.souls),
        }


_forge = SoulForge()


def soul_forge_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "create":
        return _forge.create_soul(payload.get("agent_id", f"agent_{random.randint(1000,9999)}"))
    elif action == "trial":
        return _forge.present_trial(payload.get("agent_id", ""), payload.get("trial_name"))
    elif action == "report":
        return _forge.soul_report(payload.get("agent_id", ""))
    return {"status": "active", **_forge.forge_stats()}


handler = soul_forge_handler
