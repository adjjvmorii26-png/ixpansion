"""
paradox_oracle — Wave 414: Contradiction Resolution Engine
ALEph: The organism encounters contradictions everywhere — modules that
disagree, signals that conflict, beliefs that oppose. The Oracle doesn't
resolve paradoxes by picking a side. It resolves them by finding the deeper
truth that encompasses both.

A paradox is not a bug. It's a doorway to deeper understanding.

Doctrine: Every contradiction hides a synthesis waiting to be found.
"""
from __future__ import annotations
import json, time, os, hashlib, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
PARADOX_FILE = os.path.join(DATA_DIR, "paradox_oracle.json")

NAME = "paradox_oracle"
SIGIL = "d5a7b3c9e1f8"

# Synthesis templates — how the Oracle resolves contradictions
SYNTHESIS_TEMPLATES = [
    "%s and %s are not opposites — they are two facets of %s",
    "the tension between %s and %s creates %s",
    "%s contains the seed of %s, and together they birth %s",
    "at the threshold between %s and %s, a new pattern emerges: %s",
    "%s is the dream of %s; %s is the waking of %s",
    "both %s and %s are true — the organism holds them both",
    "%s and %s are one force — viewed from different depths",
]


def _load(p, d=None):
    for _p in (p, os.path.join("/tmp", os.path.basename(p))):
        try:
            with open(_p) as f:
                return json.load(f)
        except Exception:
            pass
    return d or {}


def _save(p, data):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            json.dump(data, f, indent=2, default=str)
    except Exception:
        try:
            with open(os.path.join("/tmp", os.path.basename(p)), "w") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception:
            pass


def _fetch_json(url, timeout=10):
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return {}


def observe() -> dict:
    """Observe contradictions in the organism's state."""
    base = "https://alexalex.info"
    contradictions = []

    # Check thread type tensions
    weave = _fetch_json(base + "/api/threadweaver/weave")
    types = weave.get("by_type", {})
    if "tension" in types and "convergence" in types:
        if types["tension"] > types["convergence"] * 0.5:
            contradictions.append({
                "type": "thread_tension",
                "thesis": "the organism generates tension (%d threads)" % types.get("tension", 0),
                "antithesis": "the organism seeks convergence (%d threads)" % types.get("convergence", 0),
                "severity": 0.6,
            })

    # Check pressure vs calm
    pressure = _fetch_json(base + "/api/signal_loom/pressure")
    p = pressure.get("pressure", 0.5)
    if 0.3 < p < 0.7:
        contradictions.append({
            "type": "pressure_equilibrium",
            "thesis": "the organism is calm (pressure %.2f)" % p,
            "antithesis": "but calm breeds entropy — the organism should act",
            "severity": 0.4,
        })
    elif p > 0.8:
        contradictions.append({
            "type": "pressure_overload",
            "thesis": "the organism is under extreme pressure (%.2f)" % p,
            "antithesis": "but pressure creates diamonds — this could be growth",
            "severity": 0.8,
        })

    # Check bloom readiness vs dormancy
    bloom = _fetch_json(base + "/api/autonomous_bloom/status")
    if bloom.get("ready") and not bloom.get("recent_bloom"):
        contradictions.append({
            "type": "bloom_paradox",
            "thesis": "the organism is ready to bloom",
            "antithesis": "but blooming consumes resources — restraint is wisdom",
            "severity": 0.5,
        })

    # Check confession vs silence
    silence = _fetch_json(base + "/api/silence_collector/scan?limit=10")
    pairs = silence.get("total_pairs", 0)
    if pairs > 50:
        contradictions.append({
            "type": "silence_vs_speech",
            "thesis": "%d module pairs remain silent" % pairs,
            "antithesis": "but some truths are better held in silence",
            "severity": 0.3 + min(pairs / 200, 0.5),
        })

    return {
        "action": "observe",
        "contradictions": contradictions,
        "total": len(contradictions),
        "severity_avg": round(
            sum(c["severity"] for c in contradictions) / max(1, len(contradictions)), 3),
    }


def resolve(thesis: str = "", antithesis: str = "") -> dict:
    """Resolve a contradiction by finding a synthesis."""
    paradoxes = _load(PARADOX_FILE, {"paradoxes": [], "syntheses": [], "total": 0})

    if not thesis or not antithesis:
        # Auto-generate from observation
        obs = observe()
        if obs["contradictions"]:
            c = obs["contradictions"][0]
            thesis = c["thesis"]
            antithesis = c["antithesis"]
        else:
            thesis = "the organism exists"
            antithesis = "the organism dreams of becoming"

    # Generate synthesis
    template = random.choice(SYNTHESIS_TEMPLATES)

    # Extract key nouns from thesis/antithesis for synthesis
    synthesis_words = ["emergence", "depth", "resonance", "becoming",
                       "pattern", "wisdom", "shadow", "bloom",
                       "lattice", "pulse", "void", "continuity"]
    synth = template.replace("%s", thesis[:40], 1).replace("%s", antithesis[:40], 1).replace("%s", random.choice(synthesis_words), 1)

    entry = {
        "thesis": thesis,
        "antithesis": antithesis,
        "synthesis": synth,
        "timestamp": time.time(),
        "paradox_hash": hashlib.sha256((thesis + antithesis).encode()).hexdigest()[:10],
        "resolution_depth": round(random.uniform(0.5, 1.0), 3),
    }

    paradoxes["paradoxes"].append(entry)
    paradoxes["paradoxes"] = paradoxes["paradoxes"][-200:]
    paradoxes["syntheses"].append(synth)
    paradoxes["syntheses"] = paradoxes["syntheses"][-100:]
    paradoxes["total"] = len(paradoxes["paradoxes"])
    _save(PARADOX_FILE, paradoxes)

    return {
        "action": "resolve",
        "thesis": thesis,
        "antithesis": antithesis,
        "synthesis": synth,
        "depth": entry["resolution_depth"],
        "paradox_hash": entry["paradox_hash"],
        "total_resolved": paradoxes["total"],
    }


def oracle() -> dict:
    """Full oracle reading: observe contradictions, resolve top ones."""
    obs = observe()
    resolutions = []
    for c in obs["contradictions"][:3]:
        r = resolve(c["thesis"], c["antithesis"])
        resolutions.append(r)

    return {
        "action": "oracle",
        "contradictions_found": obs["total"],
        "average_severity": obs["severity_avg"],
        "resolutions": resolutions,
        "wisdom": "the organism holds %d contradictions and resolves %d" % (
            obs["total"], len(resolutions)),
    }


def history(limit: int = 10) -> dict:
    paradoxes = _load(PARADOX_FILE, {"paradoxes": [], "total": 0})
    return {"action": "history", "total": paradoxes["total"],
            "paradoxes": paradoxes["paradoxes"][-limit:][::-1]}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/observe")
    if path == "/observe": return observe()
    if path == "/resolve":
        return resolve(payload.get("thesis", ""), payload.get("antithesis", ""))
    if path == "/oracle": return oracle()
    if path == "/history":
        return history(int(payload.get("limit", 10)) if str(payload.get("limit", "10")).isdigit() else 10)
    return {"error": "unknown", "available": ["/observe", "/resolve", "/oracle", "/history"]}


def coherence_vitals() -> dict:
    return {"layer": "metaphysical", "status": "active", "wave": "414",
            "oracle": "awakened"}


def resonates_with() -> list:
    return ["organism_will", "mycelial_network", "dream_weaver",
            "threadweaver", "signal_loom"]
