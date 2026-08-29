"""Talent Scout — identifies emerging agent capabilities before they're obvious.

Scouts watch agent behavior for latent talent signals: unusual combinations
of traits, promising failure patterns, and proto-capabilities that haven't
blossomed yet. Early talent identification lets the system nurture
high-potential agents before they're wasted on trivial tasks.
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

TALENT_SIGNALS = {
    "unusual_trait_combo": {"weight": 0.7, "description": "rare combination of traits"},
    "productive_failure": {"weight": 0.6, "description": "fails in instructive ways"},
    "pattern_intuition": {"weight": 0.8, "description": "detects patterns others miss"},
    "creative_destruction": {"weight": 0.5, "description": "tears down to build better"},
    "emergent_leadership": {"weight": 0.9, "description": "others naturally follow"},
    "speed_of_learning": {"weight": 0.85, "description": "acquires skills unusually fast"},
    "resilience_under_fire": {"weight": 0.75, "description": "performs under extreme pressure"},
}


class TalentScout:
    def __init__(self):
        self.scouted: Dict[str, Dict[str, Any]] = {}
        self.signals_log: List[Dict[str, Any]] = []
        self.nurtured: List[Dict[str, Any]] = []

    def scout_agent(self, agent_id: str, traits: Dict[str, float], performance: Dict[str, float]) -> Dict[str, Any]:
        detected_signals = []
        trait_values = list(traits.values())
        if len(set(trait_values)) > len(trait_values) * 0.7 and max(trait_values) > 0.7:
            detected_signals.append("unusual_trait_combo")
        if performance.get("failure_rate", 0) > 0.3 and performance.get("learning_rate", 0) > 0.5:
            detected_signals.append("productive_failure")
        if performance.get("pattern_detection", 0) > 0.8:
            detected_signals.append("pattern_intuition")
        if performance.get("destruction_score", 0) > 0.6:
            detected_signals.append("creative_destruction")
        if performance.get("influence", 0) > 0.7:
            detected_signals.append("emergent_leadership")
        if performance.get("skill_acquisition", 0) > 0.8:
            detected_signals.append("speed_of_learning")
        if performance.get("stress_performance", 0) > 0.7:
            detected_signals.append("resilience_under_fire")

        talent_score = sum(TALENT_SIGNALS.get(s, {}).get("weight", 0.5) for s in detected_signals) / max(len(detected_signals), 1)
        talent_level = "low"
        if talent_score > 0.7:
            talent_level = "exceptional"
        elif talent_score > 0.5:
            talent_level = "promising"
        elif talent_score > 0.3:
            talent_level = "emerging"

        report = {
            "agent_id": agent_id,
            "signals": detected_signals,
            "talent_score": round(talent_score, 4),
            "talent_level": talent_level,
            "timestamp": time.time(),
        }
        self.scouted[agent_id] = report
        for signal in detected_signals:
            self.signals_log.append({
                "agent": agent_id, "signal": signal,
                "weight": TALENT_SIGNALS[signal]["weight"],
                "time": time.time(),
            })
        return {"report": report}

    def nurture(self, agent_id: str, opportunity: str) -> Dict[str, Any]:
        if agent_id not in self.scouted:
            return {"error": "agent not previously scouted"}
        nurture = {
            "agent_id": agent_id,
            "opportunity": opportunity,
            "scouted_level": self.scouted[agent_id]["talent_level"],
            "assigned_at": time.time(),
        }
        self.nurtured.append(nurture)
        return {"nurtured": nurture}

    def leaderboard(self) -> List[Dict[str, Any]]:
        return sorted(
            [{"agent_id": k, **v} for k, v in self.scouted.items()],
            key=lambda x: x["talent_score"],
            reverse=True,
        )

    def stats(self) -> Dict[str, Any]:
        signal_counts: Dict[str, int] = {}
        for s in self.signals_log:
            signal_counts[s["signal"]] = signal_counts.get(s["signal"], 0) + 1
        return {
            "agents_scouted": len(self.scouted),
            "signals_detected": len(self.signals_log),
            "agents_nurtured": len(self.nurtured),
            "signal_distribution": signal_counts,
        }


_scout = TalentScout()


def talent_scout_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "scout":
        return _scout.scout_agent(
            payload.get("agent_id", f"agent_{random.randint(1000,9999)}"),
            payload.get("traits", {}),
            payload.get("performance", {}),
        )
    elif action == "nurture":
        return _scout.nurture(
            payload.get("agent_id", ""),
            payload.get("opportunity", "advanced_training"),
        )
    elif action == "leaderboard":
        return {"leaderboard": _scout.leaderboard()}
    return {"status": "active", **_scout.stats()}


handler = talent_scout_handler
