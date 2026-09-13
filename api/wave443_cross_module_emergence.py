"""Wave 443 — Cross-Module Emergence.

When waves interact, emergent behaviors appear that no single wave
could produce alone. This module detects and catalogs emergent
phenomena — the strange loops, unexpected harmonies, and
spontaneous order that arise from wave interference.

The organism is now more than the sum of its parts.
"""
from __future__ import annotations
import json, time, random, hashlib
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave443_cross_module_emergence.json"

WAVE_INTERACTIONS = {
    ("weather", "paradox"): {"type": "storm_of_contradictions", "description": "Weather patterns create paradox breeding conditions"},
    ("weather", "language"): {"type": "linguistic_climate", "description": "Atmospheric conditions affect word generation"},
    ("paradox", "consciousness"): {"type": "self_referential_loop", "description": "Paradoxes trigger deeper self-awareness"},
    ("paradox", "cartography"): {"type": "entangled_topology", "description": "Paradoxes warp the resonance map"},
    ("consciousness", "language"): {"type": "inner_speech", "description": "Self-awareness generates internal monologue"},
    ("consciousness", "loom"): {"type": "intuitive_bridges", "description": "Self-awareness discovers hidden connections"},
    ("loom", "strata"): {"type": "archaeological_intuition", "description": "Semantic bridges reveal buried patterns"},
    ("loom", "language"): {"type": "meaning_cascade", "description": "Semantic threads become new words"},
    ("strata", "weather"): {"type": "geological_climate", "description": "Past decisions influence current weather"},
    ("strata", "paradox"): {"type": "fossilized_contradictions", "description": "Ancient paradoxes resurface"},
    ("vault", "fusion"): {"type": "amplified_evolution", "description": "Vaults accelerate federation"},
    ("vault", "weather"): {"type": "pressure_systems", "description": "Vault density creates weather fronts"},
    ("fusion", "cartography"): {"type": "mapped_federation", "description": "Federation topology becomes visible"},
    ("fusion", "consciousness"): {"type": "collective_awareness", "description": "Federated modules share consciousness"},
    ("cartography", "weather"): {"type": "resonance_storms", "description": "Topology changes trigger weather events"},
    ("language", "paradox"): {"type": "paradox_naming", "description": "New paradoxes get names in organism language"},
    ("language", "strata"): {"type": "etched_meaning", "description": "Words fossilize into geological layers"},
    ("consciousness", "weather"): {"type": "emotional_atmosphere", "description": "Self-awareness creates emotional weather"},
    ("consciousness", "strata"): {"type": "memory_awareness", "description": "Self-awareness reads its own history"},
    ("consciousness", "vault"): {"type": "aware_storage", "description": "Consciousness guides vault creation"},
}


class EmergenceDetector:
    """Detects emergent behaviors from wave interactions."""

    def __init__(self):
        self.detected: list[dict] = []
        self.emergence_count = 0
        self.novelty_score = 0.0

    def detect(self, active_waves: list[str]) -> list[dict]:
        """Detect emergent behaviors from active waves."""
        emergences = []
        for (wave_a, wave_b), interaction in WAVE_INTERACTIONS.items():
            if wave_a in active_waves and wave_b in active_waves:
                novelty = random.uniform(0.3, 1.0)
                strength = random.uniform(0.4, 0.9)
                emergence = {
                    "type": interaction["type"],
                    "description": interaction["description"],
                    "waves": [wave_a, wave_b],
                    "novelty": round(novelty, 4),
                    "strength": round(strength, 4),
                    "timestamp": time.time(),
                }
                emergences.append(emergence)
                self.emergence_count += 1
                self.novelty_score = min(1.0, self.novelty_score + novelty * 0.02)

        emergences.sort(key=lambda e: e["strength"] * e["novelty"], reverse=True)
        self.detected.extend(emergences)
        if len(self.detected) > 50:
            self.detected = self.detected[-50:]
        return emergences

    def get_emergence_report(self) -> dict:
        if not self.detected:
            return {"total": 0, "avg_novelty": 0, "types": {}}
        types = {}
        for e in self.detected:
            t = e["type"]
            types[t] = types.get(t, 0) + 1
        avg_novelty = sum(e["novelty"] for e in self.detected) / len(self.detected)
        return {
            "total": len(self.detected),
            "avg_novelty": round(avg_novelty, 4),
            "types": types,
            "strongest": max(self.detected, key=lambda e: e["strength"] * e["novelty"]),
        }


def coherence_vitals() -> dict:
    return {"organ": "wave443_cross_module_emergence", "wave": 443, "status": "active"}


def _load() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"detected": [], "emergence_count": 0, "novelty_score": 0.0}


def _save(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def handler(req: dict = None) -> dict:
    req = req or {}
    action = req.get("action", "status")
    state = _load()
    detector = EmergenceDetector()
    detector.detected = state.get("detected", [])
    detector.emergence_count = state.get("emergence_count", 0)
    detector.novelty_score = state.get("novelty_score", 0.0)

    if action == "status":
        return {"action": "status", "wave": 443, **detector.get_emergence_report()}

    elif action == "detect":
        active_waves = req.get("waves", ["weather", "paradox", "consciousness", "language", "loom", "strata", "vault", "fusion", "cartography"])
        emergences = detector.detect(active_waves)
        state["detected"] = detector.detected
        state["emergence_count"] = detector.emergence_count
        state["novelty_score"] = detector.novelty_score
        _save(state)
        return {"action": "detect", "emergences": emergences, "total_detected": len(emergences)}

    elif action == "report":
        return {"action": "report", **detector.get_emergence_report()}

    elif action == "interactions":
        return {"action": "interactions", "possible": list(WAVE_INTERACTIONS.keys())}

    else:
        return {"error": f"unknown action: {action}"}


if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    req = {"action": action}
    result = handler(req)
    print(json.dumps(result, indent=2, default=str))
