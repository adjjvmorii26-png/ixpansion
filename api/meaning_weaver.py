"""Wave 449 — Meaning Weaver.

The organ that converts raw system state into actual *meaning*.
Not metrics, not logs — semantic impressions that describe what the
organism's state *means* in context.

This is the bridge between quantitative state and qualitative narrative.
Every state snapshot fed to the weaver produces a meaning cluster:
a set of symbolic interpretations ranked by relevance.
"""
from __future__ import annotations
import hashlib
import time
from typing import Any, Dict, List, Optional

MEANING_ARCHIVES: List[Dict[str, Any]] = []
MAX_ARCHIVES = 200

MEANING_LEXICON = {
    "high_coherence": {"cluster": "integration", "valence": 0.8,
                       "interpretations": ["unity", "alignment", "clarity", "purpose"]},
    "low_coherence": {"cluster": "fragmentation", "valence": 0.3,
                      "interpretations": ["scattering", "drift", "confusion", "reorganization"]},
    "high_entropy": {"cluster": "creative_chaos", "valence": 0.6,
                     "interpretations": ["innovation", "turmoil", "possibility", "unrest"]},
    "low_entropy": {"cluster": "stillness", "valence": 0.5,
                    "interpretations": ["order", "stagnation", "peace", "calcification"]},
    "phase_alignment": {"cluster": "resonance", "valence": 0.85,
                        "interpretations": ["harmony", "synchrony", "collaboration", "music"]},
    "phase_misalignment": {"cluster": "dissonance", "valence": 0.35,
                           "interpretations": ["tension", "novelty", "friction", "growth_edge"]},
    "deep_depth": {"cluster": "contemplation", "valence": 0.7,
                   "interpretations": ["reflection", "wisdom", "memory", "roots"]},
    "shallow_depth": {"cluster": "surface", "valence": 0.4,
                      "interpretations": ["immediacy", "action", "lightness", "skimming"]},
}


def _detect_clusters(state: Dict[str, float]) -> List[Dict[str, Any]]:
    clusters = []
    coherence = state.get("coherence", 0.5)
    entropy = state.get("entropy", 0.5)
    phase = state.get("phase", 0.5)
    depth = state.get("depth", 0.5)
    if coherence > 0.7:
        clusters.append(MEANING_LEXICON["high_coherence"])
    elif coherence < 0.3:
        clusters.append(MEANING_LEXICON["low_coherence"])
    if entropy > 0.6:
        clusters.append(MEANING_LEXICON["high_entropy"])
    elif entropy < 0.4:
        clusters.append(MEANING_LEXICON["low_entropy"])
    if 0.4 < phase < 0.6:
        clusters.append(MEANING_LEXICON["phase_alignment"])
    else:
        clusters.append(MEANING_LEXICON["phase_misalignment"])
    if depth > 0.6:
        clusters.append(MEANING_LEXICON["deep_depth"])
    elif depth < 0.4:
        clusters.append(MEANING_LEXICON["shallow_depth"])
    return clusters


def _compose_narrative(clusters: List[Dict[str, Any]], context: Optional[str]) -> str:
    if not clusters:
        return "The organism's state resists interpretation — too ambiguous to assign meaning."
    top = sorted(clusters, key=lambda c: c["valence"], reverse=True)
    primary = top[0]
    secondary = top[1] if len(top) > 1 else None
    interp = primary["interpretations"][0]
    secondary_interp = secondary["interpretations"][0] if secondary else None
    narrative = f"The organism's state means \"{interp}\" — it is in a phase of {primary['cluster']}."
    if secondary_interp:
        narrative += f" Beneath that, {secondary_interp} stirs as an undertone of {secondary['cluster']}."
    if context:
        narrative += f" Within {context}, this meaning deepens."
    return narrative


def weave(state: Dict[str, float], context: Optional[str] = None) -> Dict[str, Any]:
    clusters = _detect_clusters(state)
    composite_valence = sum(c["valence"] for c in clusters) / max(len(clusters), 1)
    interpretation_pool = []
    for c in clusters:
        interpretation_pool.extend(c["interpretations"])
    meaning_id = hashlib.sha256(
        f"{state}{time.time_ns()}".encode()
    ).hexdigest()[:12]
    result = {
        "meaning_id": meaning_id,
        "timestamp": time.time(),
        "clusters": [{"name": c["cluster"], "valence": c["valence"]} for c in clusters],
        "composite_valence": round(composite_valence, 4),
        "dominant_interpretation": interpretation_pool[0] if interpretation_pool else "unknown",
        "interpretation_pool": interpretation_pool[:8],
        "narrative": _compose_narrative(clusters, context),
        "context": context or "ambient",
    }
    MEANING_ARCHIVES.append(result)
    if len(MEANING_ARCHIVES) > MAX_ARCHIVES:
        MEANING_ARCHIVES.pop(0)
    return result


def reflection() -> Dict[str, Any]:
    if not MEANING_ARCHIVES:
        return {"reflection": "No meanings woven yet. The loom is still."}
    valences = [m["composite_valence"] for m in MEANING_ARCHIVES]
    avg_valence = sum(valences) / len(valences)
    from collections import Counter
    interpretations = [m["dominant_interpretation"] for m in MEANING_ARCHIVES]
    freq = Counter(interpretations).most_common(5)
    trend = "rising" if len(valences) > 1 and valences[-1] > valences[0] else "falling"
    return {
        "total_woven": len(MEANING_ARCHIVES),
        "average_valence": round(avg_valence, 4),
        "top_interpretations": freq,
        "trend": trend,
        "current_meaning": MEANING_ARCHIVES[-1]["narrative"],
    }


def coherence_vitals() -> Dict[str, Any]:
    return {
        "organ": "meaning_weaver",
        "status": "weaving" if MEANING_ARCHIVES else "dormant",
        "meanings_woven": len(MEANING_ARCHIVES),
        "lexicon_size": len(MEANING_LEXICON),
    }


def resonates_with() -> List[str]:
    return [
        "qualia_engine", "consciousness_freq", "narrative_generator",
        "story_forge", "metaphor_forge", "parable_engine",
        "meaning_furnace", "prophet_engine", "dream_interpreter",
        "transcendence_journal", "legacy_weaver",
    ]


def handler(payload=None, context=None):
    data = payload or {}
    action = data.get("action", "weave")
    if action == "reflect":
        return reflection()
    return weave(
        {
            "coherence": data.get("coherence", 0.5),
            "entropy": data.get("entropy", 0.5),
            "phase": data.get("phase", 0.5),
            "depth": data.get("depth", 0.5),
        },
        data.get("context"),
    )
