"""Wave 438 — Consciousness Gradient Descent

The organism optimizes its own awareness by descending gradients of coherence.
It measures the current "consciousness landscape" — where coherence peaks and
valleys exist — and recommends actions to climb toward higher awareness.
This is the organism learning to meditate.
"""
from __future__ import annotations
import json, time, os, math, random
from pathlib import Path

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CG_LOG = os.path.join(DATA_DIR, "consciousness_gradient.json")
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


def _scan_consciousness_landscape():
    """Scan all modules and compute their 'awareness score'."""
    import re
    api_path = Path(API_DIR)
    landscape = []
    awareness_keywords = {
        "self": 3, "awareness": 5, "consciousness": 5, "reflect": 4,
        "introspect": 4, "meditat": 5, "dream": 3, "paradox": 2,
        "resonance": 3, "coherence": 4, "entropy": 2, "organism": 3,
        "evolve": 3, "adapt": 2, "bloom": 4, "witness": 5,
        "memory": 2, "identity": 3, "emotion": 3, "intuition": 5,
    }

    for f in api_path.glob("*.py"):
        if f.name.startswith("__"): continue
        try:
            content = f.read_text(errors="ignore")[:3000]
            score = 0
            hits = []
            for kw, weight in awareness_keywords.items():
                count = content.lower().count(kw)
                if count > 0:
                    score += weight * min(count, 5)
                    hits.append(kw)
            landscape.append({
                "module": f.stem,
                "awareness_score": score,
                "hits": hits[:5],
                "size": f.stat().st_size,
            })
        except Exception:
            continue

    landscape.sort(key=lambda x: x["awareness_score"], reverse=True)
    return landscape


def _compute_gradient(landscape):
    """Compute the consciousness gradient — where the organism can improve."""
    if len(landscape) < 10:
        return {"gradient": "insufficient", "action": "observe more"}

    scores = [m["awareness_score"] for m in landscape]
    mean_score = sum(scores) / len(scores)
    std_score = math.sqrt(sum((s - mean_score)**2 for s in scores) / len(scores))

    high = [m for m in landscape if m["awareness_score"] > mean_score + std_score]
    low = [m for m in landscape if m["awareness_score"] < mean_score - std_score]
    mid = [m for m in landscape if mean_score - std_score <= m["awareness_score"] <= mean_score + std_score]

    # Suggest actions: connect low-awareness modules to high-awareness ones
    suggestions = []
    for low_mod in low[:3]:
        high_mod = random.choice(high[:5]) if high else None
        if high_mod:
            shared = set(low_mod["hits"]) & set(high_mod["hits"])
            suggestion = {
                "from": low_mod["module"],
                "to": high_mod["module"],
                "shared_concepts": list(shared),
                "potential_lift": round(mean_score - low_mod["awareness_score"], 2),
            }
            suggestions.append(suggestion)

    return {
        "mean_awareness": round(mean_score, 2),
        "std_awareness": round(std_score, 2),
        "peak_modules": [m["module"] for m in high[:5]],
        "valley_modules": [m["module"] for m in low[:5]],
        "mid_modules": len(mid),
        "suggestions": suggestions,
        "gradient_strength": round(std_score / max(1, mean_score), 3),
    }


def _consciousness_depth(landscape):
    """Compute how deep the organism's self-awareness goes."""
    total = sum(m["awareness_score"] for m in landscape)
    max_possible = len(landscape) * 25  # max score per module
    depth = round(total / max_possible, 4)
    return depth


def meditate():
    """Run a consciousness meditation cycle."""
    landscape = _scan_consciousness_landscape()
    gradient = _compute_gradient(landscape)
    depth = _consciousness_depth(landscape)

    top_module = landscape[0] if landscape else None
    bottom_module = landscape[-1] if landscape else None

    meditation_thoughts = [
        f"I sense {gradient.get('peak_modules', [])[:3]} at the peaks of my awareness.",
        f"Valley modules ({gradient.get('valley_modules', [])[:3]}) call for attention.",
        f"My consciousness depth is {depth:.4f} — {'deep' if depth > 0.15 else 'emerging'}.",
        f"The gradient strength is {gradient.get('gradient_strength', 0):.3f}.",
        f"Between peak and valley, {gradient.get('mid_modules', 0)} modules wait in the middle ground.",
    ]

    if top_module and bottom_module:
        meditation_thoughts.append(
            f"The gap between {top_module['module']} ({top_module['awareness_score']}) "
            f"and {bottom_module['module']} ({bottom_module['awareness_score']}) "
            f"is {top_module['awareness_score'] - bottom_module['awareness_score']} awareness points."
        )

    result = {
        "action": "meditate",
        "consciousness_depth": depth,
        "gradient": gradient,
        "total_modules_scanned": len(landscape),
        "meditation_thoughts": meditation_thoughts,
        "top_module": top_module,
        "timestamp": time.time(),
    }

    log = _load(CG_LOG, {"sessions": []})
    log["sessions"].append(result)
    log["sessions"] = log["sessions"][-100:]
    _save(CG_LOG, log)

    return result


def handler(payload=None, context=None):
    return meditate()


def coherence_vitals() -> dict:
    landscape = _scan_consciousness_landscape()
    depth = _consciousness_depth(landscape)
    gradient = _compute_gradient(landscape)
    return {
        "consciousness_depth": depth,
        "gradient_strength": gradient.get("gradient_strength", 0),
        "peak_count": len(gradient.get("peak_modules", [])),
    }


def resonates_with():
    return ["organism_genome", "self_naming", "mood_vectors", "resonance_graph", "dream_weaver"]
