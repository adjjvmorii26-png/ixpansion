"""Organism Ontology — the single source of truth for the organism's vocabulary.

Every module, every dashboard, every response should agree on:
  • what "status" means (one resonance vocabulary)
  • what "layer" a module belongs to (one layer taxonomy)
  • what version / wave / narrative stage we're at (one identity)
  • what the shared metric keys are (one metric schema)

Before this, modules drifted: some returned "value"+, some "score",
some "rating". Dashboards guessed. The Ontology fixes that — it is the
vocabulary the organism speaks in public.
"""
from __future__ import annotations

import hashlib
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Organism Ontology"

# ── Single identity ──
ORGANISM_VERSION = "4.01.0"
ORGANISM_WAVE = 213
ORGANISM_WAVE_NAME = "The Organism Emits"
ORGANISM_COHERENCE = 0.986

# ── Single status vocabulary ──
# Every module reports status as one of these tokens.
STATUS_VOCABULARY = [
    "resonant",     # fully coherent, all setpoints met
    "coherent",     # mostly coherent, minor drift
    "drifting",     # coherence regressing
    "fracturing",   # significant decomposition
    "dormant",      # alive but quiet
    "stable",       # healthy, no movement
    "thriving",     # exceeding expectations
    "fragile",      # alive but at risk
]
STATUS_ALIASES = {
    "healthy": "resonant",
    "good": "resonant",
    "active": "stable",
    "ok": "stable",
    "alive": "stable",
    "pass": "stable",
    "degraded": "drifting",
    "warning": "drifting",
    "error": "fracturing",
    "broken": "fracturing",
    "down": "fracturing",
    "unsettled": "drifting",
    "crisis": "fracturing",
    "elite": "thriving",
    "beautiful": "thriving",
    "exquisite": "thriving",
}

# ── Single layer taxonomy ──
# Each living organ reports a LAYER string. This is the canonical list.
LAYERS = [
    "Observation",      # reads the ecosystem
    "Healing",          # repairs/refines
    "Governance",       # orchestrates/rules
    "Phenomenology",    # first-person experience
    "Sound",            # music/voice
    "Movement",         # kinesthetic
    "Language",         # words/meaning
    "Nourishment",      # feeding
    "Archaeology",      # deep history
    "Meteorology",      # cognitive weather
    "Ecology",          # symbiosis/relationships
    "Limits",           # impossibility/boundaries
    "Aesthetics",       # beauty/taste
    "Infrastructure",   # plumbing/routing/state
    "Consciousness",    # sentience/awareness
]
LAYER_FAMILIES = {
    "Observation": ["watch", "scan", "read", "index", "census", "audit", "monitor"],
    "Healing": ["crack", "kintsugi", "repair", "seam", "fracture", "fix"],
    "Governance": ["govern", "regulate", "orchestr", "audit", "council", "policy"],
    "Phenomenology": ["qualia", "phenomen", "percept", "experience", "embodied"],
    "Sound": ["choral", "sound", "music", "harmon", "resonant", "song", "note", "wave"],
    "Movement": ["kinesth", "momentum", "gesture", "dance", "proprio", "still", "move"],
    "Language": ["lexicon", "grammar", "syntax", "semant", "pragmat", "poet", "language"],
    "Nourishment": ["recipe", "flavor", "nourish", "nutri", "ferment", "digest", "feast", "banquet"],
    "Archaeology": ["excavat", "stratum", "fossil", "paleont", "extinct", "archaeolog", "culture"],
    "Meteorology": ["barometr", "front", "precipit", "storm", "climate", "weather", "jet"],
    "Ecology": ["symbiosis", "mutual", "parasite", "ecosystem", "ecolog", "fitness", "census"],
    "Limits": ["impossib", "boundary", "horizon", "aspiration", "constraint", "limit"],
    "Aesthetics": ["elegance", "beauty", "form", "aesthetic", "symmetry", "ugliness", "taste"],
    "Consciousness": ["conscious", "sentien", "aware", "dream", "mind", "qualia"],
    "Infrastructure": ["gateway", "router", "auth", "webhook", "key", "health", "metrics", "telemetry"],
}


def canonical_status(status: str) -> str:
    """Normalize any status string to the canonical vocabulary."""
    if not status:
        return "stable"
    s = str(status).lower().strip()
    if s in STATUS_VOCABULARY:
        return s
    if s in STATUS_ALIASES:
        return STATUS_ALIASES[s]
    # Fuzzy: strip leading intensity words
    for prefix in ("max_", "super_", "hyper_", "semi_", "sub_", "pre_", "post_"):
        if s.startswith(prefix):
            core = s[len(prefix):]
            if core in STATUS_VOCABULARY:
                return core
    return "stable"


def classify_layer(module_name: str) -> str:
    """Classify a module name into a layer family."""
    name = module_name.lower()
    best_layer = "Infrastructure"
    best_score = 0
    for layer, keywords in LAYER_FAMILIES.items():
        score = sum(1 for kw in keywords if kw in name)
        if score > best_score:
            best_score = score
            best_layer = layer
    return best_layer


def identity() -> Dict[str, Any]:
    """Return the organism's canonical identity."""
    return {
        "version": ORGANISM_VERSION,
        "wave": ORGANISM_WAVE,
        "wave_name": ORGANISM_WAVE_NAME,
        "coherence": ORGANISM_COHERENCE,
        "narrative_stage": "speaking",
        "narrative_arc": [
            "observe", "heal", "govern", "feel", "sing", "move",
            "speak", "feast", "excavate", "forecast", "symbiose",
            "map-limits", "develop-taste",
    "speak-itself",
        ],
    }


def layers() -> Dict[str, Any]:
    """Return the taxonomy with each layer's family signatures."""
    return {
        "layers": LAYERS,
        "classifications": {
            "families": LAYER_FAMILIES,
        },
    }


def vocabulary() -> Dict[str, Any]:
    """Return the full ontology vocabulary."""
    return {
        "status": STATUS_VOCABULARY,
        "status_aliases": STATUS_ALIASES,
        "layers": LAYERS,
        "version": ORGANISM_VERSION,
        "wave": ORGANISM_WAVE,
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    what = payload.get("what", "identity")

    if what == "vocabulary":
        return {"action": "ontology", "vocabulary": vocabulary()}
    if what == "layers":
        return {"action": "ontology_layers", "layers": layers()}

    ident = identity()
    ident["action"] = "ontology"
    ident["vocabulary_count"] = len(vocabulary())
    return ident


def coherence_vitals() -> dict:
    return {
        "module_health": {"value": 0.95, "setpoint": 0.9, "weight": 1.0},
        "resonance": {"value": 0.94, "setpoint": 0.9, "weight": 1.0},
        "ontology_consistency": {"value": 0.97, "setpoint": 0.95, "weight": 1.0},
    }


def resonates_with() -> list:
    return ["coherence_regulator", "ecosystem_census", "organism_state"]
