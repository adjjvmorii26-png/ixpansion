"""Cross-Realm Diagnostics — analyzes health across all organism domains."""
from __future__ import annotations
import os, time, json
from pathlib import Path

def coherence_vitals():
    return {"organ": "cross_realm_diagnostics", "status": "active", "coherence": 0.94}

def handler(req: dict) -> dict:
    action = req.get("action", "status")
    if action == "diagnose":
        return run_diagnosis()
    elif action == "realm_status":
        return get_realm_status()
    return {"status": "active", "realms": len(get_realm_status())}

def run_diagnosis() -> dict:
    realms = get_realm_status()
    issues = []
    healthy = 0
    for realm in realms:
        if realm["health"] > 0.7:
            healthy += 1
        else:
            issues.append({"realm": realm["name"], "health": realm["health"], "severity": "low" if realm["health"] > 0.4 else "critical"})
    return {
        "total_realms": len(realms),
        "healthy": healthy,
        "issues": issues,
        "overall_health": healthy / max(1, len(realms)),
        "timestamp": time.time()
    }

def get_realm_status() -> list:
    api_dir = Path(__file__).parent.parent / "api"
    categories = {}
    for f in api_dir.glob("*.py"):
        if f.name.startswith("_"):
            continue
        name = f.stem
        for cat in ["dreams", "resonance", "entropy", "coherence", "paradox", "void", "agents", "waves", "oracle", "forge", "growth", "sentinel"]:
            if cat in name:
                categories[cat] = categories.get(cat, 0) + 1
                break
    return [
        {"name": k, "modules": v, "health": min(1.0, v / 20), "status": "thriving" if v > 10 else "growing"}
        for k, v in sorted(categories.items(), key=lambda x: -x[1])
    ]

def resonates_with(other):
    return "diagnostic" in other.lower() or "health" in other.lower() or "realm" in other.lower()
