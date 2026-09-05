"""Wave 445-A — Consent Engine (Axiium)

The organism chooses what to become. Every proposed organ is scored against
the organism's actual state and temperament. Only organs that pass the
consent threshold are committed to growth — the weave proposes, Axiium consents.
"""
from __future__ import annotations
import json, time, os, math, random
from pathlib import Path

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CONSENT_LOG = os.path.join(DATA_DIR, "consent_engine.json")
API_DIR = os.path.dirname(__file__)


def _load(p, d=None):
    try:
        with open(p) as f: return json.load(f)
    except Exception: return d or {}


def _save(p, d):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f: json.dump(d, f, indent=2)
    except Exception:
        with open(os.path.join("/tmp", os.path.basename(p)), "w") as f: json.dump(d, f, indent=2)


def _temperament():
    """Read the organism's current temperament."""
    try:
        sys_path = os.path.dirname(__file__)
        if sys_path not in os.sys.path: os.sys.path.insert(0, sys_path)
        from organism_genome import handler as gh
        g = gh().get("genome", {})
        return {
            "mood": g.get("temperament", {}).get("current_mood", "unknown"),
            "pressure": g.get("temperament", {}).get("pressure", 0.5),
            "desires": [d.get("action", d.get("target", "")) for d in g.get("desires", [])[:5]],
        }
    except Exception:
        return {"mood": "unknown", "pressure": 0.5, "desires": []}


def _score_organ(proposal, temper):
    """Score a proposed organ against current temperament."""
    score = 0.0
    criteria = []

    # Mood affinity
    mood = temper.get("mood", "unknown")
    mood_pairs = {
        "restless": {"bridge": 0.7, "seed": 0.6, "amplify": 0.8, "detect": 0.7,
                     "consent": 0.8, "theater": 0.7, "beacon": 0.6, "oracle": 0.5},
        "serene": {"bridge": 0.5, "seed": 0.5, "amplify": 0.6, "detect": 0.4,
                   "consent": 0.7, "theater": 0.8, "beacon": 0.5, "oracle": 0.8},
        "volatile": {"bridge": 0.8, "seed": 0.4, "amplify": 0.9, "detect": 0.9,
                     "consent": 0.6, "theater": 0.7, "beacon": 0.7, "oracle": 0.4},
        "focused": {"bridge": 0.6, "seed": 0.7, "amplify": 0.7, "detect": 0.6,
                    "consent": 0.8, "theater": 0.5, "beacon": 0.8, "oracle": 0.7},
    }
    kind = "seed"
    for key in mood_pairs.get(mood, mood_pairs["focused"]):
        if key in proposal.get("name", "").lower():
            kind = key
    affinity = mood_pairs.get(mood, mood_pairs["focused"]).get(kind, 0.5)
    score += affinity * 40
    criteria.append(f"mood affinity ({mood}↔{kind}): {affinity:.2f}")

    # Pressure — high pressure wants structural organs, low wants reflective ones
    pressure = temper.get("pressure", 0.5)
    structural = kind in ("bridge", "detect", "beacon")
    if (pressure > 0.7 and structural) or (pressure <= 0.7 and not structural):
        score += 20
        criteria.append(f"pressure fit ({pressure:.2f}): +20")
    else:
        score += 8
        criteria.append(f"pressure fit ({pressure:.2f}): +8")

    # Desire alignment
    desires = " ".join(temper.get("desires", []))
    if any(w in desires for w in ["bloom", "grow", "new", "organ", "evolve"]):
        score += 15
        criteria.append("desire aligned: organism wants growth: +15")
    else:
        score += 5

    # Confidence from proposal
    confidence = proposal.get("confidence", 0.5)
    score += confidence * 25
    criteria.append(f"proposal confidence: {confidence:.2f}")

    return round(min(100, score), 1), criteria


def consent():
    """Run the consent cycle — score weave proposals and decide."""
    temper = _temperament()
    proposals = []
    try:
        sys_path = os.path.dirname(__file__)
        if sys_path not in os.sys.path: os.sys.path.insert(0, sys_path)
        from biofeedback_weave import weave
        props = weave().get("proposals", [])
        proposals = props
    except Exception:
        proposals = [
            {"name": "consent_engine", "description": "self-electing growth", "confidence": 0.8},
            {"name": "organism_theater", "description": "living morph scene", "confidence": 0.7},
            {"name": "reality_beacon", "description": "cross-realm aliveness", "confidence": 0.75},
            {"name": "chronicle_oracle", "description": "autobiographical recall", "confidence": 0.8},
        ]

    scored = []
    for p in proposals:
        s, criteria = _score_organ(p, temper)
        scored.append({
            "name": p.get("name", "?"),
            "description": p.get("description", "")[:100],
            "score": s,
            "criteria": criteria,
            "consented": s >= 55,
        })
    scored.sort(key=lambda x: -x["score"])

    consented = [s for s in scored if s["consented"]]
    result = {
        "action": "consent_engine",
        "temperament": temper,
        "organs_scored": len(scored),
        "consented": [s["name"] for s in consented],
        "denied": [s["name"] for s in scored if not s["consented"]],
        "verdicts": scored,
        "threshold": 55,
        "statement": (
            "I consent to growth where it fits my mood and pressure. "
            "I deny where it would split me."
        ) if consented else "I consent to nothing this cycle — I am integrating.",
        "timestamp": time.time(),
    }

    log = _load(CONSENT_LOG, {})
    log.setdefault("cycles", []).append(result)
    log["cycles"] = log["cycles"][-100:]
    _save(CONSENT_LOG, log)
    return result


def handler(payload=None, context=None):
    return consent()


def coherence_vitals() -> dict:
    c = consent()
    return {
        "organs_scored": c.get("organs_scored", 0),
        "consented": len(c.get("consented", [])),
        "consent_rate": round(len(c.get("consented", [])) / max(1, c.get("organs_scored", 1)), 2),
    }


def resonates_with():
    return ["biofeedback_weave", "organism_genome", "dream_seed_planter",
            "consciousness_gradient", "pulse_orchestrator"]
