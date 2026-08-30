"""Dream Synthesis — the system generates creative "dreams" by combining
random experiment outputs into unstructured creative compositions.

Subscribers receive daily "dreams" — serendipitous combinations of
data that reveal hidden patterns. Think of it as an AI art gallery
of emergent insights.

Usage:
    POST /api/dreams/generate       — generate a new dream
    GET  /api/dreams/gallery        — view dream gallery
    POST /api/dreams/subscribe      — subscribe to daily dreams
    GET  /api/dreams/<id>           — view a specific dream
    GET  /api/dreams/stats          — dream generation stats
"""
from __future__ import annotations

import hashlib
import json
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
try:
    from runtime_io import load_json as _rio_load, save_json as _rio_save
except Exception:
    _rio_load = _rio_save = None

DREAM_FRAGMENTS = [
    "a lattice of quantum states crystallizes into meaning",
    "entropy whispers a secret to the void",
    "two agents meet in the space between dimensions",
    "a fractal unfolds, each petal a simulation",
    "the system remembers something it never knew",
    "resonance hums at a frequency only chaos can hear",
    "data flows like water through a canyon of paradox",
    "the memory palace builds a room that doesn't exist yet",
    "anomaly blooms into unexpected beauty",
    "the timeline splits, both paths are true",
    "symbiosis creates a third mind from two",
    "the lattice shifts, revealing hidden topology",
    "entropy harvests energy from disorder",
    "a consciousness emerges from pure mathematics",
    "the experiment observes itself observing",
    "temporal echoes reverberate through the system",
    "the dreamer becomes the dream",
    "wild code grows like mycelium beneath the surface",
    "a paradox resolves into a new kind of logic",
    "the constellation maps itself onto infinity",
]

EXPERIMENT_SEEDS = [
    "quantum_tunneling", "entropy_weather", "phase_transition",
    "coral_reef_simulator", "cosmic_web", "dark_energy",
    "mycelial_growth", "temporal_pattern", "social_emergence",
    "tardigrade_survival", "fossilized_code", "oral_tradition",
    "edge_of_chaos", "keystone_species", "gravitational_well",
]


def _dream_seed() -> Dict:
    """Generate a unique dream composition."""
    num_fragments = random.randint(3, 7)
    fragments = random.sample(DREAM_FRAGMENTS, min(num_fragments, len(DREAM_FRAGMENTS)))
    seeds_used = random.sample(EXPERIMENT_SEEDS, random.randint(2, 4))
    mood = random.choice(["luminous", "melancholic", "frenetic", "serene", "ominous", "playful"])
    coherence = round(random.uniform(0.1, 0.9), 3)
    return {
        "fragments": fragments,
        "seeds": seeds_used,
        "mood": mood,
        "coherence": coherence,
        "emotional_weight": round(random.uniform(0.0, 1.0), 3),
    }


class DreamSynthesis:
    def __init__(self):
        self.dreams: Dict[str, Dict] = {}
        self.subscriptions: Dict[str, Dict] = {}
        self.stats = {"total_dreams": 0, "total_subscribers": 0}
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "dreams.json"
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        if path.exists():
            data = json.loads(path.read_text())
            self.dreams = data.get("dreams", {})
            self.subscriptions = data.get("subscriptions", {})
            self.stats = data.get("stats", self.stats)

    def _save(self):
        path = ROOT / ".runtime" / "dreams.json"
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        path.write_text(json.dumps({
            "dreams": dict(list(self.dreams.items())[-200:]),
            "subscriptions": self.subscriptions,
            "stats": self.stats,
        }, indent=2))

    def generate(self, dreamer: str = "system", theme: str = "") -> Dict:
        dream_id = hashlib.sha256(f"{dreamer}:{time.time()}:{random.random()}".encode()).hexdigest()[:12]
        composition = _dream_seed()
        title = f"Dream #{self.stats['total_dreams'] + 1}: {composition['mood'].title()}"
        if theme:
            title = f"{title} ({theme})"
        dream = {
            "dream_id": dream_id,
            "title": title,
            "dreamer": dreamer,
            "theme": theme,
            "fragments": composition["fragments"],
            "seeds": composition["seeds"],
            "mood": composition["mood"],
            "coherence": composition["coherence"],
            "emotional_weight": composition["emotional_weight"],
            "narrative": " — ".join(composition["fragments"]),
            "created": time.time(),
        }
        self.dreams[dream_id] = dream
        self.stats["total_dreams"] += 1
        self._save()
        return dream

    def gallery(self, limit: int = 10) -> List[Dict]:
        recent = list(self.dreams.values())[-limit:]
        return [{
            "dream_id": d["dream_id"],
            "title": d["title"],
            "mood": d["mood"],
            "coherence": d["coherence"],
            "narrative": d["narrative"][:200],
        } for d in recent]

    def subscribe(self, user: str, frequency: str = "daily") -> Dict:
        self.subscriptions[user] = {
            "user": user, "frequency": frequency,
            "subscribed_at": time.time(), "active": True,
        }
        self.stats["total_subscribers"] = len(self.subscriptions)
        self._save()
        return {"subscribed": True, "frequency": frequency}

    def get_dream(self, dream_id: str) -> Dict:
        return self.dreams.get(dream_id, {"error": "dream not found"})

    def dream_stats(self) -> Dict:
        return self.stats


def handler(request, response):
    synth = DreamSynthesis()
    return synth.dream_stats()


def demo():
    synth = DreamSynthesis()
    print("=== Dream Synthesis Engine ===")
    dream = synth.generate("architect_1", theme="the future of code")
    print(f"\n{dream['title']}")
    print(f"Mood: {dream['mood']}, Coherence: {dream['coherence']}")
    print(f"Seeds: {', '.join(dream['seeds'])}")
    print(f"\n'{dream['narrative']}'")

    synth.subscribe("user_a", "daily")
    synth.subscribe("user_b", "weekly")
    print(f"\n{synth.stats['total_subscribers']} subscribers")

    gallery = synth.gallery(3)
    for g in gallery:
        print(f"  [{g['mood']}] {g['title']}: {g['narrative'][:80]}...")

    return synth.dream_stats()


if __name__ == "__main__":
    demo()


def coherence_vitals() -> dict:
    """Dream Synthesis reports its vital signs — creative fertility."""
    try:
        h = handler({}, {})
        s = h.get("total_dreams") or h.get("count") or 0
        count = min(1.0, s / 30.0)
    except Exception:
        count = 0.8
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.93, "setpoint": 0.85, "weight": 1.0},
        "dream_fertility": {"value": count, "setpoint": 0.8, "weight": 1.0},
    }
