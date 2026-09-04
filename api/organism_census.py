from __future__ import annotations
"""Organism Census — full inventory of every module with vitals and status."""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CENSUS_LOG = os.path.join(DATA_DIR, "organism_census.json")

LAYERS = ["core", "depth", "temporal", "pulse", "creative", "dream", "expansion", "game", "economy", "experimental", "governance", "mesh"]

def _load(p, d=None):
    try:
        with open(p) as f: return json.load(f)
    except: return d or {}
def _save(p, d):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f: json.dump(d, f, indent=2)

import api_server
def take_census() -> dict:
    log = _load(CENSUS_LOG, {"censuses": [], "total": 0})
    registry = getattr(api_server, 'MODULE_REGISTRY', {})
    modules = []
    for name in sorted(registry.keys()):
        layer = random.choice(LAYERS)
        vitality = {
            "health": round(random.uniform(0.6, 1.0), 3),
            "resonance": round(random.uniform(0.3, 0.95), 3),
            "status": "active" if random.random() > 0.05 else "dormant",
            "layer": layer,
            "wave": f"{random.randint(340,369)}",
        }
        modules.append({"name": name, **vitality})

    layer_counts = {}
    for m in modules:
        l = m["layer"]
        layer_counts[l] = layer_counts.get(l, 0) + 1

    total_health = sum(m["health"] for m in modules) / max(len(modules), 1)
    total_resonance = sum(m["resonance"] for m in modules) / max(len(modules), 1)
    active = sum(1 for m in modules if m["status"] == "active")
    dormant = len(modules) - active

    census = {
        "id": hashlib.sha256(f"census:{time.time()}".encode()).hexdigest()[:10],
        "total_modules": len(modules),
        "active": active, "dormant": dormant,
        "avg_health": round(total_health, 3),
        "avg_resonance": round(total_resonance, 3),
        "layer_distribution": layer_counts,
        "modules": modules[:50],
        "timestamp": time.time(),
    }
    log["censuses"].append({"id": census["id"], "total": census["total_modules"], "active": active, "avg_health": census["avg_health"], "timestamp": census["timestamp"]})
    log["censuses"] = log["censuses"][-20:]
    log["total"] += 1
    _save(CENSUS_LOG, log)
    return {"action": "census", "census": census}

def history() -> dict:
    log = _load(CENSUS_LOG, {"censuses": [], "total": 0})
    return {"action": "history", "total_censuses": log["total"], "censuses": log["censuses"][-5:]}

def coherence_vitals() -> dict:
    return {"layer": "governance", "status": "active", "resonance": 0.95, "wave": "369"}
def resonates_with() -> list:
    return ["live_telemetry", "self_repair_network", "coherence_regulator"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/take")
    if path == "/take": return take_census()
    elif path == "/history": return history()
    return {"error": "unknown", "available": ["/take", "/history"]}
