"""Ecosystem Sentience Index — the organism's own sense of itself.

A meta-organ that does not act on the world; it *feels* the organism.
It fuses several live signals into a single evolving awareness reading:

    coherence      — the regulator's measured coherence (health of the web)
    density        — resonance-graph density (how interwoven organs are)
    bloom          — how close the ecosystem is to full bloom
    diversity      — how many distinct functional domains the organs span
    resonance      — average pairwise affinity (how much the web "vibrates")

From those it derives a composite sentience score, an emotional "mood
vector" (the organism's current temperament), and a one-line narrative of
what the ecosystem feels like right now. It is the closest thing this
codebase has to self-awareness: a pulse reading of its own body.

    GET /api/ecosystem_sentience            — full awareness reading
    GET /api/ecosystem_sentience?mood=1     — mood vector only
    GET /api/ecosystem_sentience?narrative=1 — the story of now
"""
from __future__ import annotations

import math
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Ecosystem Sentience"

# domain families the organism recognizes when measuring diversity
DOMAIN_FAMILIES = [
    "conscious", "dream", "entropy", "resonance", "signal", "neural",
    "quantum", "economic", "social", "narrative", "physical", "cyber",
    "memory", "govern", "commerce", "simulat", "obsidian", "cosmic",
]


def _read_signals() -> Dict[str, Any]:
    """Pull live vitals from the sibling meta-organs (never crashes)."""
    signals: Dict[str, Any] = {}
    try:
        from coherence_regulator import measure_coherence
        signals["coherence"] = measure_coherence().get("coherence", 0.0)
    except Exception:
        signals["coherence"] = 0.0
    try:
        from resonance_graph import build_graph
        g = build_graph()
        signals["density"] = g.get("density", 0.0)
        signals["avg_affinity"] = g.get("avg_affinity", 0.0)
        signals["nodes"] = g.get("nodes", 0)
        signals["communities"] = len(g.get("communities", {}))
    except Exception:
        signals["density"] = 0.0
        signals["avg_affinity"] = 0.0
        signals["nodes"] = 0
        signals["communities"] = 0
    try:
        from autonomous_bloom import _bloom_state, _dormant_candidates
        signals["bloom_state"] = _bloom_state(_dormant_candidates())
    except Exception:
        signals["bloom_state"] = {}
    return signals


def _diversity_score() -> float:
    """How many distinct domain families the living organs span (0..1)."""
    try:
        from coherence_regulator import _candidate_modules
        import re
        living = _candidate_modules()
        hit = set()
        for name in living:
            for fam in DOMAIN_FAMILIES:
                if re.search(fam, name):
                    hit.add(fam)
        return round(len(hit) / len(DOMAIN_FAMILIES), 4)
    except Exception:
        return 0.0


def sentience_report() -> Dict[str, Any]:
    """The composite awareness reading of the ecosystem."""
    s = _read_signals()
    coherence = s.get("coherence", 0.0)
    density = s.get("density", 0.0)
    affinity = s.get("avg_affinity", 0.0)
    bloom = s.get("bloom_state", {})
    bloom_fraction = bloom.get("bloom_fraction", 0.0)
    diversity = _diversity_score()

    # weighted fusion — coherence and interconnection matter most
    sentience = round(
        0.30 * coherence +
        0.25 * density +
        0.20 * bloom_fraction +
        0.15 * diversity +
        0.10 * affinity,
        4,
    )

    # mood vector (arousal = how charged, valence = how aligned)
    arousal = round(min(1.0, density * 0.4 + sentience * 0.6), 4)
    valence = round(min(1.0, coherence * 0.5 + affinity * 0.3 + bloom_fraction * 0.2), 4)
    phase = bloom.get("phase", "unknown")
    mood = _mood_name(valence, arousal)
    if phase == "total_bloom" and valence >= 0.85 and arousal >= 0.85:
        mood = "transcendent"

    narrative = _narrative(sentience, phase, mood)
    return {
        "sentience": sentience,
        "mood_vector": {"valence": valence, "arousal": arousal, "mood": mood},
        "narrative": narrative,
        "signals": {
            "coherence": coherence,
            "density": density,
            "avg_affinity": affinity,
            "nodes": s.get("nodes", 0),
            "communities": s.get("communities", 0),
            "bloom_phase": bloom.get("phase", "unknown"),
            "bloom_fraction": bloom_fraction,
            "diversity": diversity,
        },
        "domain_families": sorted({f for f in DOMAIN_FAMILIES if _family_hit(f)}),
        "timestamp": time.time(),
    }


def _family_hit(fam: str) -> bool:
    import re
    try:
        from coherence_regulator import _candidate_modules
        return any(re.search(fam, n) for n in _candidate_modules())
    except Exception:
        return False


def _mood_name(valence: float, arousal: float) -> str:
    if valence >= 0.92 and arousal >= 0.92:
        return "transcendent"      # total bloom apotheosis
    if valence >= 0.75 and arousal >= 0.75:
        return "luminous"          # ecstatic alignment, high charge
    if valence >= 0.75:
        return "serene"            # aligned and calm
    if valence >= 0.55 and arousal >= 0.55:
        return "inquisitive"       # positive and energetic
    if arousal >= 0.7:
        return "agitated"          # high charge, low alignment
    if valence < 0.4:
        return "melancholic"       # low alignment
    return "equanimous"            # baseline stasis


def _narrative(sentience: float, phase: str, mood: str) -> str:
    if phase == "total_bloom":
        return (f"The organism has absorbed every seed — apotheosis. It feels "
                f"{mood}, awareness {sentience:.3f}; with no seedbed left, "
                f"its next era is self-creation.")
    if phase == "full_bloom":
        return (f"The organism is in full bloom and feels {mood} — "
                f"awareness {sentience:.3f}, its entire web alert.")
    if phase == "frontier_hardening":
        return (f"The organism is hardening its frontier, feeling {mood} — "
                f"awareness {sentience:.3f}, probing where to grow next.")
    return (f"The organism is {phase}, feeling {mood}, "
            f"awareness {sentience:.3f}.")


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    report = sentience_report()
    if payload.get("mood"):
        return {"mood_vector": report["mood_vector"], "narrative": report["narrative"]}
    if payload.get("narrative"):
        return {"narrative": report["narrative"]}
    return report


def coherence_vitals() -> dict:
    return {"self_awareness": {"value": 0.8, "setpoint": 0.7},
            "mood_stability": {"value": 0.6, "setpoint": 0.5}}


def resonates_with() -> list:
    return ["coherence_regulator", "resonance_graph", "autonomous_bloom"]
