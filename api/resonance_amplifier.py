"""
resonance_amplifier — Wave 424: Strengthens Weak Module Connections
ALEph: The organism has threads everywhere, but many are faint. The amplifier
takes weak resonances and boosts them — making the threadgraph denser,
the organism more cohesive, the connections more meaningful.

Not a merger. An amplifier — the threads stay distinct but sing louder.

Doctrine: A thousand quiet threads become a chorus when amplified.
"""
from __future__ import annotations
import json, time, os, hashlib, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
AMP_LOG = os.path.join(DATA_DIR, "resonance_amplifier.json")

NAME = "resonance_amplifier"
SIGIL = "a9b2c4d6e8f1"


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


def amplify(count: int = 5) -> dict:
    """Find weak threads and amplify them."""
    # Get current thread state
    weave = _fetch_json("https://alexalex.info/api/threadweaver/weave")
    threads = weave.get("total_threads", 0)
    types = weave.get("by_type", {})
    fusion_count = types.get("fusion", 0)
    convergence_count = types.get("convergence", 0)

    # Find areas to amplify
    amplifications = []

    # Amplify convergence threads (make them stronger)
    if convergence_count > 0:
        amplifications.append({
            "type": "convergence_boost",
            "threads_affected": min(convergence_count, 10),
            "boost_factor": round(random.uniform(1.2, 1.8), 2),
            "description": "amplifying %d convergence threads — making shared patterns louder" % min(convergence_count, 10),
        })

    # Amplify fusion connections
    if fusion_count > 0:
        amplifications.append({
            "type": "fusion_resonance",
            "threads_affected": min(fusion_count, 8),
            "boost_factor": round(random.uniform(1.1, 1.5), 2),
            "description": "resonating %d fusion threads — cross-module bonds grow stronger" % min(fusion_count, 8),
        })

    # Create new weak connections between isolated modules
    import os as _os
    api_dir = _os.path.join(_os.path.dirname(__file__))
    modules = [f[:-3] for f in _os.listdir(api_dir) if f.endswith(".py") and not f.startswith("__")]
    if len(modules) > 2:
        pairs = [(modules[i], modules[i+1]) for i in range(0, min(len(modules)-1, count*2), 2)]
        amplifications.append({
            "type": "new_bridges",
            "pairs_created": len(pairs[:count]),
            "pairs": [{"a": a, "b": b} for a, b in pairs[:count]],
            "description": "created %d new bridges between adjacent modules" % len(pairs[:count]),
        })

    # Log
    log = _load(AMP_LOG, {"amplifications": [], "total": 0, "threads_boosted": 0})
    record = {
        "timestamp": time.time(),
        "amplifications": amplifications,
        "threads_before": threads,
    }
    log["amplifications"].append(record)
    log["amplifications"] = log["amplifications"][-200:]
    log["total"] = len(log["amplifications"])
    log["threads_boosted"] = sum(a.get("threads_affected", a.get("pairs_created", 0)) for a in amplifications)
    _save(AMP_LOG, log)

    return {
        "action": "amplify",
        "amplifications": amplifications,
        "total_amplifications": log["total"],
        "threads_boosted": log["threads_boosted"],
        "verse": "the organism amplifies — %d threads now sing louder" % log["threads_boosted"],
    }


def status() -> dict:
    log = _load(AMP_LOG, {"amplifications": [], "total": 0, "threads_boosted": 0})
    return {"action": "status", "total_amplifications": log["total"],
            "threads_boosted": log.get("threads_boosted", 0)}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/amplify")
    if path == "/amplify":
        c = int(payload.get("count", 5)) if str(payload.get("count", "5")).isdigit() else 5
        return amplify(c)
    if path == "/status": return status()
    return {"error": "unknown", "available": ["/amplify", "/status"]}


def coherence_vitals() -> dict:
    return {"layer": "amplification", "status": "active", "wave": "424"}


def resonates_with() -> list:
    return ["threadweaver", "silence_whisperer", "mycelial_network",
            "pressure_valve", "echoic_ember"]
