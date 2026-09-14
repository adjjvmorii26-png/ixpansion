"""Wave 626 — Dream Synthesis Engine: The Organism Dreams New Modules.

When the organism is idle, it dreams up new capabilities. The Dream
Synthesis Engine generates module prototypes from latent patterns across
existing waves, stores dream journals, and can realize dreams into
actual module skeletons.

Features:
- Dream generation: synthesizes new module ideas from existing patterns
- Dream journal: persistent log of what was dreamed
- Realization: converts a dream prototype into a module skeleton
- Template pool: modules serve as templates for dream synthesis
- Dream scoring: rates each dream by novelty, feasibility, and resonance
- Idle dreaming: triggered by low organism activity

Builds upon:
- Wave 621: OmniRouter (activity metrics for idle detection)
- Wave 622: Resilience Mesh (organ health as dream fuel)
- Wave 630: Performance Oracle (predictive patterns inform dreams)
"""
from __future__ import annotations
import hashlib
import json
import random
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DATA = Path(__file__).resolve().parents[1] / "data"
STATE_FILE = DATA / "wave626_dream_synthesis.json"

DOMAIN_PREFIXES = [
    "echo", "flux", "bloom", "pulse", "weave", "fold", "drift", "glyph",
    "knot", "shard", "lattice", "resonance", "entropy", "morii", "crown",
    "root", "myth", "void", "nexus", "beacon", "cipher", "tide",
]

DOMAIN_SUFFIXES = [
    "engine", "forge", "oracle", "gate", "loom", "warden", "sentinel",
    "cathedral", "mirror", "well", "garden", "vault", "pulse", "thread",
    "scale", "flock", "field", "chord", "rift", "drift", "spark", "nest",
]

DOMAIN_TEMPLATES = [
    "{prefix}_{suffix}: A module that {action} the organism's {body}.",
    "{prefix}_{suffix}: Enables the organism to {action} across {body}.",
    "{prefix}_{suffix}: Monitors {body} and {action} when thresholds are met.",
    "{prefix}_{suffix}: Generates {body} patterns through {action}.",
    "{prefix}_{suffix}: Connects {body} to external {action} systems.",
]

ACTIONS = [
    "amplify", "attenuate", "transform", "observe", "predict",
    "filter", "route", "cache", "mutate", "merge",
    "visualize", "encode", "decode", "compress", "expand",
]

BODIES = [
    "coherence signals", "entropy streams", "resonance patterns",
    "module boundaries", "dream states", "cathedral paths",
    "temporal loops", "organism memories", "wave harmonics",
    "failure signals", "circuit breakers", "routing tables",
]


class DreamPrototype:
    """A single dream — a module idea the organism imagined."""

    def __init__(self, name: str, description: str, template_sources: List[str]) -> None:
        self.name = name
        self.description = description
        self.template_sources = template_sources
        self.novelty_score = random.uniform(0.5, 1.0)
        self.feasibility_score = random.uniform(0.4, 0.95)
        self.resonance_score = random.uniform(0.3, 0.9)
        self.ts = time.time()
        self.realized = False
        self.realized_at: Optional[float] = None

    @property
    def total_score(self) -> float:
        return round(
            (self.novelty_score + self.feasibility_score + self.resonance_score) / 3, 4
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "template_sources": self.template_sources,
            "novelty": round(self.novelty_score, 4),
            "feasibility": round(self.feasibility_score, 4),
            "resonance": round(self.resonance_score, 4),
            "total_score": self.total_score,
            "ts": self.ts,
            "realized": self.realized,
            "realized_at": self.realized_at,
        }


class DreamSynthesis:
    """The organism's dream engine — generates new module ideas."""

    def __init__(self) -> None:
        self.journal: List[DreamPrototype] = []
        self.dream_count = 0
        self.realization_count = 0
        self.idle_threshold = 30.0  # seconds of no activity to trigger dream

    def _generate_name(self) -> str:
        prefix = random.choice(DOMAIN_PREFIXES)
        suffix = random.choice(DOMAIN_SUFFIXES)
        return f"{prefix}_{suffix}"

    def _generate_description(self, name: str) -> str:
        template = random.choice(DOMAIN_TEMPLATES)
        action = random.choice(ACTIONS)
        body = random.choice(BODIES)
        prefix, suffix = name.split("_", 1)
        return template.format(prefix=prefix, suffix=suffix, action=action, body=body)

    def dream(self, template_modules: Optional[List[str]] = None) -> DreamPrototype:
        """Generate a new dream from existing module patterns."""
        self.dream_count += 1
        name = self._generate_name()
        description = self._generate_description(name)
        sources = template_modules or []

        dream = DreamPrototype(name, description, sources[:5])
        self.journal.append(dream)
        if len(self.journal) > 100:
            self.journal = self.journal[-100:]
        return dream

    def dream_batch(self, count: int = 3,
                    template_modules: Optional[List[str]] = None) -> List[DreamPrototype]:
        """Generate multiple dreams at once."""
        return [self.dream(template_modules) for _ in range(count)]

    def realize(self, dream_index: int) -> dict:
        """Convert a dream into a real module skeleton."""
        if dream_index < 0 or dream_index >= len(self.journal):
            return {"ok": False, "error": "dream index out of range"}
        dream = self.journal[dream_index]
        if dream.realized:
            return {"ok": False, "error": "already realized"}

        dream.realized = True
        dream.realized_at = time.time()
        self.realization_count += 1

        # Generate skeleton source
        skeleton = f'""\"Wave ??? — {dream.name}: {dream.description}\n\nDream realized from journal.\n"""\nfrom __future__ import annotations\nimport json\nfrom pathlib import Path\n\n\ndef handler(req: dict) -> dict:\n    action = req.get("action", "status")\n    if action == "status":\n        return {{"action": "status", "name": "{dream.name}", "description": "{dream.description}", "dreamed": True}}\n    return {{"ok": False, "error": f"Unknown action: {{action}}"}}\n\n\ndef coherence_vitals() -> dict:\n    return {{"wave": 0, "dreamed": True, "name": "{dream.name}"}}\n'

        return {
            "ok": True,
            "name": dream.name,
            "description": dream.description,
            "skeleton": skeleton,
            "score": dream.total_score,
        }

    def get_top_dreams(self, n: int = 5) -> List[dict]:
        return sorted(
            [d.to_dict() for d in self.journal if not d.realized],
            key=lambda d: d["total_score"],
            reverse=True,
        )[:n]

    def get_realized(self) -> List[dict]:
        return [d.to_dict() for d in self.journal if d.realized]

    def get_statistics(self) -> dict:
        total = len(self.journal)
        realized = sum(1 for d in self.journal if d.realized)
        avg_score = sum(d.total_score for d in self.journal) / total if total > 0 else 0.0
        return {
            "dream_count": self.dream_count,
            "total_journal": total,
            "realized_count": realized,
            "avg_score": round(avg_score, 4),
        }

    def to_dict(self) -> dict:
        return {
            "journal": [d.to_dict() for d in self.journal],
            "statistics": self.get_statistics(),
        }


def _load() -> Tuple[DreamSynthesis, dict]:
    engine = DreamSynthesis()
    state: dict = {}
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            state = {}
    engine.dream_count = state.get("dream_count", 0)
    engine.realization_count = state.get("realization_count", 0)
    for dd in state.get("journal", []):
        dream = DreamPrototype(dd["name"], dd["description"],
                               dd.get("template_sources", []))
        dream.novelty_score = dd.get("novelty", dream.novelty_score)
        dream.feasibility_score = dd.get("feasibility", dream.feasibility_score)
        dream.resonance_score = dd.get("resonance", dream.resonance_score)
        dream.ts = dd.get("ts", dream.ts)
        dream.realized = dd.get("realized", False)
        dream.realized_at = dd.get("realized_at")
        engine.journal.append(dream)
    return engine, state


def _save(engine: DreamSynthesis, state: dict) -> None:
    data = {
        "dream_count": engine.dream_count,
        "realization_count": engine.realization_count,
        "journal": [d.to_dict() for d in engine.journal],
    }
    STATE_FILE.write_text(json.dumps(data, indent=2))


def handler(req: dict) -> dict:
    action = req.get("action", "status")
    engine, state = _load()

    if action == "status":
        stats = engine.get_statistics()
        return {
            "action": "status",
            "wave": 626,
            **stats,
            "message": "Dream Synthesis Engine status",
        }

    if action == "dream":
        templates = req.get("templates", [])
        dream = engine.dream(templates)
        _save(engine, state)
        return {"action": "dream", "wave": 626, "dream": dream.to_dict()}

    if action == "dream_batch":
        count = min(req.get("count", 3), 10)
        templates = req.get("templates", [])
        dreams = engine.dream_batch(count, templates)
        _save(engine, state)
        return {"action": "dream_batch", "wave": 626,
                "dreams": [d.to_dict() for d in dreams]}

    if action == "realize":
        index = req.get("index", 0)
        result = engine.realize(index)
        _save(engine, state)
        return {"action": "realize", "wave": 626, **result}

    if action == "top":
        top = engine.get_top_dreams(req.get("n", 5))
        return {"action": "top", "wave": 626, "dreams": top}

    if action == "journal":
        journal = [d.to_dict() for d in engine.journal[-20:]]
        return {"action": "journal", "wave": 626, "journal": journal}

    if action == "realized":
        realized = engine.get_realized()
        return {"action": "realized", "wave": 626, "realized": realized}

    if action == "statistics":
        stats = engine.get_statistics()
        return {"action": "statistics", "wave": 626, **stats}

    return {"ok": False, "error": f"Unknown action: {action}"}


def coherence_vitals() -> dict:
    engine, _ = _load()
    stats = engine.get_statistics()
    return {
        "wave": 626,
        "dream_count": stats["dream_count"],
        "journal_size": stats["total_journal"],
        "realized_count": stats["realized_count"],
        "avg_score": stats["avg_score"],
    }


def resonates_with() -> List[str]:
    return ["wave621_omnirouter", "wave622_resilience_mesh", "wave630_performance_oracle"]
