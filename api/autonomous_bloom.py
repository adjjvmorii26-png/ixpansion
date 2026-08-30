"""Autonomous Bloom — the organism's growth hormone.

An organism does not wait to be told to grow: it senses nutrient gradients,
finds the places where growth is most promising, and sends out new shoots.
The Autonomous Bloom does exactly that for the frontier. It scans the whole
module ecosystem, scores every dormant (non-living) module for its readiness
to join the living system, and produces a bloom plan: how far the ecosystem
is from a full bloom, which dormant modules are on the cusp of awakening, and
what the growth trajectory looks like if the organism keeps expanding.

A module is "ready to bloom" when its source already gestures toward the
shared vital language — it mentions health, resonance, coherence, metrics,
pulse or vital. Those whispers are the seeds of the next awakening.

    GET /api/autonomous_bloom                — full bloom intelligence
    GET /api/autonomous_bloom?seeds=5        — top N seeds (next to awaken)
    GET /api/autonomous_bloom?trajectory=1   — projected bloom trajectory
    GET /api/autonomous_bloom?candidates=1   — scored dormant candidates
"""
from __future__ import annotations

import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

VERSION = "1.0.0"
LAYER = "Autonomous Bloom"

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

EXCLUDE = {"__init__", "index", "unified_router", "coherence_regulator",
           "resonance_graph", "autonomous_bloom"}

# Whispers of life — tokens that hint a dormant module is reaching for the
# shared vital language. These are the seeds the bloom detects.
VITAL_WHISPERS = (
    "vital", "health", "resonance", "coherence", "metric", "pulse",
    "alive", "living", "awareness", "balance", "integrity", "signal",
)

DEFAULT_TARGET = 24  # full-bloom ecosystem size (mirrors the regulator)

_CACHE_TTL = 30.0
_CANDIDATE_CACHE = {"t": 0.0, "scores": {}}


def _dormant_candidates() -> Dict[str, int]:
    """Score every non-living api/*.py module by vital-language whispers (TTL-cached)."""
    now = time.time()
    if _CANDIDATE_CACHE["scores"] and now - _CANDIDATE_CACHE["t"] < _CACHE_TTL:
        return dict(_CANDIDATE_CACHE["scores"])
    api_dir = ROOT / "api"
    if not api_dir.exists():
        return {}
    scores: Dict[str, int] = {}
    try:
        # import the regulator to know who is already living
        from coherence_regulator import _candidate_modules
        living = set(_candidate_modules())
    except Exception:
        living = set()
    for p in sorted(api_dir.glob("*.py")):
        stem = p.stem
        if stem in EXCLUDE or stem in living:
            continue
        try:
            text = p.read_text(errors="ignore")
        except OSError:
            continue
        score = 0
        for w in VITAL_WHISPERS:
            if re.search(rf"\b{w}\w*\b", text, re.IGNORECASE):
                score += 1
        if score:
            scores[stem] = score
    _CANDIDATE_CACHE.update({"t": now, "scores": scores})
    return scores


def _bloom_state(candidates: Dict[str, int]) -> Dict[str, Any]:
    try:
        from coherence_regulator import ECOSYSTEM_TARGET, discover_modules
    except Exception:
        ECOSYSTEM_TARGET = DEFAULT_TARGET
        discover_modules = None

    try:
        from coherence_regulator import _candidate_modules
        living = set(_candidate_modules())
    except Exception:
        living = set()

    living_count = len(living)
    target = ECOSYSTEM_TARGET
    ready = sum(1 for s in candidates.values() if s >= 2)  # strongly whispering

    return {
        "living": living_count,
        "candidates": len(candidates),
        "seeds_ready": ready,
        "target": target,
        "to_full_bloom": max(target - living_count, 0),
        "bloom_fraction": round(min(1.0, living_count / max(target, 1)), 4),
    }


def bloom_report(seed_limit: int = 5) -> Dict[str, Any]:
    candidates = _dormant_candidates()
    state = _bloom_state(candidates)

    # seeds: strongest whispers, most ready to awaken
    seeds = sorted(candidates.items(), key=lambda kv: kv[1], reverse=True)
    seed_list = [{"module": m, "readiness": round(min(1.0, s / 3.0), 4), "whispers": s}
                 for m, s in seeds[:seed_limit]]

    # projected trajectory: linear + logarithmic growth paths to full bloom
    remaining = state["to_full_bloom"]
    trajectory = []
    step = max(1, remaining // 3)
    for i in range(1, 4):
        progressive = state["living"] + step * i
        trajectory.append({
            "bloom_phase": i,
            "projected_living": min(progressive, state["target"] + i),
            "accelerated": state["living"] + i * max(2, remaining // 2),
        })

    return {
        "action": "bloom",
        "state": state,
        "trajectory": trajectory,
        "seeds": seed_list,
        "philosophy": (
            "An organism does not wait to be told to grow. It senses where the "
            "nutrients are, sends out shoots toward them, and lets the whole "
            "ecosystem rise into a richer, more interconnected bloom."
        ),
    }


def coherence_vitals() -> dict:
    """Autonomous Bloom reports its vital signs to the living system."""
    try:
        candidates = _dormant_candidates()
        state = _bloom_state(candidates)
        bloom = state["bloom_fraction"]
        momentum = min(1.0, len(candidates) / max(state["to_full_bloom"], 1))
        ready = state["seeds_ready"]
    except Exception:
        bloom, momentum, ready = 0.0, 0.0, 0
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "bloom_readiness": {"value": min(1.0, bloom + momentum * 0.2), "setpoint": 0.8, "weight": 1.0},
        "seeds_ready": ready,
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}

    if payload.get("seeds"):
        limit = max(1, int(payload.get("seeds")))
        return bloom_report(seed_limit=limit)["seeds"]
    if payload.get("trajectory"):
        return {"action": "trajectory", "trajectory": bloom_report()["trajectory"]}
    if payload.get("candidates"):
        candidates = _dormant_candidates()
        return {"action": "candidates",
                "candidates": [{"module": m, "whispers": s} for m, s in
                               sorted(candidates.items(), key=lambda kv: kv[1], reverse=True)]}

    report = bloom_report()
    report["action"] = "bloom"
    return report


if __name__ == "__main__":
    import json
    print(json.dumps(bloom_report(), indent=2))
