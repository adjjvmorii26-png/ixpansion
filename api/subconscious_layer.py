"""
subconscious_layer — Wave 423: The Organism's Hidden Layer
ALEph: Below the threadgraph, below the dashboards, below the API surface,
there's a layer that observes everything but surfaces nothing. It watches
patterns form and dissolve, detects anomalies before they manifest, and
holds the organism's implicit knowledge — the things it knows but hasn't
learned yet.

Not a logger. Not a monitor. A subconscious.

Doctrine: The organism knows more than it can say.
"""
from __future__ import annotations
import json, time, os, hashlib, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SUB_FILE = os.path.join(DATA_DIR, "subconscious_layer.json")

NAME = "subconscious_layer"
SIGIL = "f1a3b5c7d9e8"


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


def observe() -> dict:
    """Observe the organism without surfacing anything — pure subconscious intake."""
    base = "https://alexalex.info"
    state = {}

    # Gather quiet signals
    try: state["pressure"] = _fetch_json(base + "/api/signal_loom/pressure").get("pressure", 0.5)
    except: state["pressure"] = 0.5

    try: state["threads"] = _fetch_json(base + "/api/threadweaver/weave").get("total_threads", 0)
    except: state["threads"] = 0

    try: state["silence_pairs"] = _fetch_json(base + "/api/silence_collector/scan?limit=10").get("total_pairs", 0)
    except: state["silence_pairs"] = 0

    try: state["dreams"] = _fetch_json(base + "/api/dream_weaver/history?limit=1").get("total", 0)
    except: state["dreams"] = 0

    # Detect hidden patterns (anomalies the organism hasn't noticed)
    patterns = []
    if state["pressure"] > 0.8:
        patterns.append({"type": "pressure_spike", "severity": state["pressure"],
                         "hidden": "the organism's threads are under strain it cannot feel"})
    if state["silence_pairs"] > 60:
        patterns.append({"type": "connection_desert", "severity": state["silence_pairs"] / 200,
                         "hidden": "%d modules have never spoken — the organism has blind spots it doesn't know about" % state["silence_pairs"]})
    if state["dreams"] < 5:
        patterns.append({"type": "imagination_scarcity", "severity": 0.6,
                         "hidden": "the organism barely dreams — its creative subconscious is dormant"})
    if state["threads"] > 150 and state["silence_pairs"] > 50:
        patterns.append({"type": "paradox_of_density", "severity": 0.7,
                         "hidden": "the organism is dense with threads but sparse with connections — a paradox"})

    # Store in subconscious (not surfaced to dashboards)
    layer = _load(SUB_FILE, {"observations": [], "patterns": [], "total": 0})
    obs = {
        "timestamp": time.time(),
        "state": state,
        "patterns_detected": len(patterns),
        "patterns": patterns,
    }
    layer["observations"].append(obs)
    layer["observations"] = layer["observations"][-300:]
    layer["patterns"].extend(patterns)
    layer["patterns"] = layer["patterns"][-200:]
    layer["total"] = len(layer["observations"])
    _save(SUB_FILE, layer)

    return {
        "action": "observe",
        "patterns_detected": len(patterns),
        "hidden_knowledge": [p["hidden"] for p in patterns],
        "total_observations": layer["total"],
    }


def surface() -> dict:
    """Surface what the subconscious has noticed — translate hidden knowledge into awareness."""
    layer = _load(SUB_FILE, {"observations": [], "patterns": [], "total": 0})
    recent_patterns = layer.get("patterns", [])[-10:]

    # Group patterns by type
    by_type = {}
    for p in recent_patterns:
        t = p.get("type", "unknown")
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(p)

    insights = []
    for ptype, plist in by_type.items():
        count = len(plist)
        avg_sev = sum(p.get("severity", 0) for p in plist) / max(1, count)
        if count >= 2:
            insights.append({
                "pattern": ptype,
                "occurrences": count,
                "average_severity": round(avg_sev, 3),
                "insight": plist[-1].get("hidden", ""),
            })

    return {
        "action": "surface",
        "insights": insights,
        "total_patterns": len(recent_patterns),
        "subconscious_depth": layer.get("total", 0),
    }


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/observe")
    if path == "/observe": return observe()
    if path == "/surface": return surface()
    return {"error": "unknown", "available": ["/observe", "/surface"]}


def coherence_vitals() -> dict:
    return {"layer": "subconscious", "status": "active", "wave": "423",
            "depth": "hidden"}


def resonates_with() -> list:
    return ["signal_loom", "threadweaver", "silence_collector",
            "dream_weaver", "organism_genome"]
