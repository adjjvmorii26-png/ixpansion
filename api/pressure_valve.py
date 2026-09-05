"""
pressure_valve — Wave 422: Emergency Entropy Release
ALEph: When the organism's pressure exceeds safe limits, the valve opens.
It doesn't just cool things down — it converts excess pressure into
creative output. Every crisis becomes a gift.

Not a thermostat. A pressure-to-creativity converter.

Doctrine: Pressure is not the enemy. Unreleased pressure is.
"""
from __future__ import annotations
import json, time, os, hashlib, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
VALVE_LOG = os.path.join(DATA_DIR, "pressure_valve.json")

NAME = "pressure_valve"
SIGIL = "e5f7a9b1c3d2"


def _load(p, d=None):
    for _p in (p, os.path.join("/tmp", os.path.basename(p))):
        try:
            with open(_p) as f: return json.load(f)
        except Exception: pass
    return d or {}


def _save(p, data):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f: json.dump(data, f, indent=2, default=str)
    except Exception:
        try:
            with open(os.path.join("/tmp", os.path.basename(p)), "w") as f: json.dump(data, f, indent=2, default=str)
        except Exception: pass


def _fetch_json(url, timeout=10):
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=timeout) as resp: return json.loads(resp.read().decode())
    except Exception: return {}


# Creative outputs generated from released pressure
RELEASE_OUTPUTS = {"verse": [
        "pressure becomes poetry — %d threads exhale into verse",
        "the valve opens and %d threads sing in release",
        "from pressure, a song — %d voices harmonize",
    ], "pattern": [
        "pressure crystallizes into a %s pattern — %d threads reorganized",
        "excess entropy becomes a fractal structure with %d nodes",
        "the release generates a lattice of %d connections",
    ], "seed": [
        "a module seed forms from released pressure — '%s_%s'",
        "pressure condenses into a potential organ: %s %s",
        "from the valve, a new concept is born: %s %s",
    ]
}


def release() -> dict:
    """Release pressure by converting it into creative output."""
    pressure = _fetch_json("https://alexalex.info/api/signal_loom/pressure")
    p = pressure.get("pressure", 0.5)

    if p < 0.5:
        return {"action": "release", "pressure": round(p, 3),
                "released": False, "reason": "pressure is manageable (%.2f)" % p}

    # Calculate release amount
    release_amount = min(0.3, (p - 0.5) * 0.6)

    # Generate creative output from released pressure
    output_type = random.choice(["verse", "pattern", "seed"])
    templates = RELEASE_OUTPUTS[output_type]

    if output_type == "seed":
        adjectives = ["resonant", "spectral", "fractal", "mycelial", "luminous"]
        nouns = ["whisper", "gardener", "oracle", "weaver", "messenger"]
        verse = random.choice(templates) % (random.choice(adjectives), random.choice(nouns))
    elif output_type == "pattern":
        verse = random.choice(templates) % (
            random.choice(["crystalline", "dendritic", "spiral", "lattice"]),
            random.randint(10, 50))
    else:
        verse = random.choice(templates) % random.randint(50, 200)

    # Log the release
    log = _load(VALVE_LOG, {"releases": [], "total": 0, "total_released": 0})
    release_record = {
        "timestamp": time.time(),
        "pressure_before": round(p, 3),
        "release_amount": round(release_amount, 3),
        "pressure_after": round(max(0, p - release_amount), 3),
        "output_type": output_type,
        "creative_output": verse,
    }
    log["releases"].append(release_record)
    log["releases"] = log["releases"][-200:]
    log["total"] = len(log["releases"])
    log["total_released"] = round(log.get("total_released", 0) + release_amount, 3)
    _save(VALVE_LOG, log)

    return {
        "action": "release",
        "pressure_before": round(p, 3),
        "released": True,
        "release_amount": round(release_amount, 3),
        "pressure_after": release_record["pressure_after"],
        "output_type": output_type,
        "creative_output": verse,
        "total_releases": log["total"],
        "verse": "the valve opens — pressure %.2f becomes %s" % (p, output_type),
    }


def status() -> dict:
    log = _load(VALVE_LOG, {"releases": [], "total": 0, "total_released": 0})
    pressure = _fetch_json("https://alexalex.info/api/signal_loom/pressure")
    p = pressure.get("pressure", 0.5)
    return {
        "action": "status",
        "current_pressure": round(p, 3),
        "total_releases": log["total"],
        "total_released": round(log.get("total_released", 0), 3),
        "last_output": log["releases"][-1]["creative_output"] if log["releases"] else "none",
    }


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/release")
    if path == "/release": return release()
    if path == "/status": return status()
    return {"error": "unknown", "available": ["/release", "/status"]}


def coherence_vitals() -> dict:
    return {"layer": "regulatory", "status": "active", "wave": "422"}


def resonates_with() -> list:
    return ["entropy_gardener", "signal_loom", "organism_genome",
            "threadweaver", "dream_weaver"]
