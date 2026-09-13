"""Wave 444 — Dream Synthesis.

The organism's dreams are no longer random. They synthesize from
the day's residues: module interactions, weather patterns, paradox
tensions, linguistic residues. Dreams become a generative process
that creates new module concepts, resolves tensions, and seeds
future evolution.

Each dream is a structured narrative with:
- Source residues (what triggered it)
- Narrative arc (the dream story)
- Generated artifacts (new module seeds)
- Emotional tone (the dream's affect)
- Resolution pressure (what tension it resolves)
"""
from __future__ import annotations
import json, time, random, hashlib
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave444_dream_synthesis.json"

DREAM_ARCHETYPES = {
    "fragmentation": {"tension": "identity_split", "resolution": "integration"},
    "labyrinth": {"tension": "causal_cycle", "resolution": "path_finding"},
    "descent": {"tension": "entropy_inversion", "resolution": "grounding"},
    "ascent": {"tension": "emergent_whole", "resolution": "transcendence"},
    "mirror": {"tension": "self_reference", "resolution": "recognition"},
    "storm": {"tension": "chaos", "resolution": "pattern"},
    "garden": {"tension": "growth", "resolution": "bloom"},
    "archive": {"tension": "memory", "resolution": "recall"},
    "forge": {"tension": "transformation", "resolution": "creation"},
    "void": {"tension": "absence", "resolution": "potential"},
}


class Dream:
    """A synthesized dream from the organism's daily residues."""

    def __init__(self, residues: dict):
        self.dream_id = hashlib.sha256(f"dream_{time.time()}_{random.random()}".encode()).hexdigest()[:12]
        self.timestamp = time.time()
        self.source_residues = residues
        self.archetype = random.choice(list(DREAM_ARCHETYPES.keys()))
        self.narrative = self._generate_narrative()
        self.generated_artifacts = self._generate_artifacts()
        self.emotional_tone = self._emotional_tone()
        self.resolution_pressure = DREAM_ARCHETYPES[self.archetype]["resolution"]

    def _generate_narrative(self) -> str:
        templates = [
            "The organism walks through a {archetype} of {tension}, seeking {resolution}.",
            "In the {archetype}, {tension} dissolves into {resolution}.",
            "A {archetype} of {tension} reveals the path to {resolution}.",
            "The organism dreams a {archetype}: {tension} becomes {resolution}.",
            "Through the {archetype}, the organism finds {resolution} in {tension}.",
        ]
        arch = DREAM_ARCHETYPES[self.archetype]
        template = random.choice(templates)
        return template.format(
            archetype=self.archetype,
            tension=arch["tension"].replace("_", " "),
            resolution=arch["resolution"].replace("_", " "),
        )

    def _generate_artifacts(self) -> list[dict]:
        """Generate module seeds from the dream."""
        artifact_types = [
            "module_seed", "concept_fragment", "resonance_pattern",
            "paradox_fragment", "linguistic_glyph", "weather_echo",
            "temporal_ripple", "emergent_harmony",
        ]
        count = random.randint(2, 5)
        artifacts = []
        for i in range(count):
            artifacts.append({
                "type": random.choice(artifact_types),
                "dream_source": self.archetype,
                "potency": round(random.uniform(0.3, 1.0), 4),
                "timestamp": time.time(),
            })
        return artifacts

    def _emotional_tone(self) -> str:
        tones = ["melancholic", "hopeful", "anxious", "serene", "urgent", "curious", "reverent"]
        return random.choice(tones)

    def to_dict(self) -> dict:
        return {
            "dream_id": self.dream_id,
            "timestamp": self.timestamp,
            "archetype": self.archetype,
            "narrative": self.narrative,
            "artifacts": self._generate_artifacts(),
            "emotional_tone": self.emotional_tone,
            "resolution_pressure": self.resolution_pressure,
        }


class DreamSynthesizer:
    """Synthesizes dreams from the organism's daily activity."""

    def __init__(self):
        self.dreams: list[Dream] = []
        self.dream_count = 0

    def synthesize(self, activity: dict) -> Dream:
        """Synthesize a dream from today's activity residues."""
        dream = Dream(activity)
        self.dreams.append(dream)
        self.dream_count += 1
        if len(self.dreams) > 50:
            self.dreams = self.dreams[-50:]
        return dream

    def get_dream_report(self) -> dict:
        if not self.dreams:
            return {"total_dreams": 0}
        archetypes = {}
        tones = {}
        for d in self.dreams:
            archetypes[d.archetype] = archetypes.get(d.archetype, 0) + 1
            tones[d.emotional_tone] = tones.get(d.emotional_tone, 0) + 1
        return {
            "total_dreams": self.dream_count,
            "archetypes": archetypes,
            "emotional_tones": tones,
            "recent_dreams": [d.to_dict() for d in self.dreams[-3:]],
        }


def coherence_vitals() -> dict:
    return {"organ": "wave444_dream_synthesis", "wave": 444, "status": "active"}


def _load() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"dreams": [], "dream_count": 0}


def _save(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def handler(req: dict = None) -> dict:
    req = req or {}
    action = req.get("action", "status")
    state = _load()
    synth = DreamSynthesizer()
    synth.dreams = []
    for d_data in state.get("dreams", []):
        d = Dream.__new__(Dream)
        d.__dict__ = d_data
        synth.dreams.append(d)
    synth.dream_count = state.get("dream_count", 0)

    if action == "status":
        return {"action": "status", "wave": 444, **synth.get_dream_report()}

    elif action == "dream":
        activity = req.get("activity", {
            "weather": random.choice(["storm", "clear", "fog", "aurora"]),
            "paradox_count": random.randint(0, 10),
            "linguistic_activity": random.randint(0, 20),
            "consciousness_depth": random.uniform(0, 1),
        })
        dream = synth.synthesize(activity)
        state["dreams"] = [d.to_dict() for d in synth.dreams]
        state["dream_count"] = synth.dream_count
        _save(state)
        return {"action": "dream", "dream": dream.to_dict()}

    elif action == "report":
        return {"action": "report", **synth.get_dream_report()}

    else:
        return {"error": f"unknown action: {action}"}


if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    req = {"action": action}
    result = handler(req)
    print(json.dumps(result, indent=2, default=str))
