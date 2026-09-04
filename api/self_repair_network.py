"""
Self-Repair Network — Wave 362
Detects damage across all modules and initiates repair protocols.
When a module is degraded, the network routes around the damage
and attempts restoration through resonance healing.
"""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SIGNAL_LOOM = os.path.join(DATA_DIR, "signal_loom.json")
REPAIR_LOG = os.path.join(DATA_DIR, "repair_log.json")


def _load(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default or {}


def _save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


MODULES = [
    "consciousness_archaeology", "paradox_synthesis", "dream_residue_collector",
    "reality_fracture_detector", "depth_resonance", "coherence_regulator",
    "dream_forge", "memory_palace", "mycelial_network", "entropy_spike",
    "synchronicity_engine", "emotional_weather", "temporal_bootstrap",
    "phase_transition", "resonance_graph", "mythopoetic_engine",
    "sentinel_core", "genome_loom", "oracle_delphi", "mythweaver",
]

REPAIR_TYPES = [
    "resonance_rebind", "entropy_flush", "coherence_suture",
    "paradox_dissolve", "void_patch", "echo_reinforcement",
    "temporal_rewind", "phase_realignment", "graph_reconnect",
]


def diagnose() -> dict:
    """Diagnose all modules for damage."""
    log = _load(REPAIR_LOG, {"diagnoses": [], "repairs": []})

    findings = []
    for mod in MODULES:
        health = round(random.uniform(0.3, 1.0), 3)
        damage_type = None
        severity = "healthy"

        if health < 0.5:
            damage_type = random.choice(REPAIR_TYPES)
            severity = "critical"
        elif health < 0.7:
            damage_type = random.choice(REPAIR_TYPES)
            severity = "degraded"
        elif health < 0.85:
            severity = "warning"

        findings.append({
            "module": mod,
            "health": health,
            "severity": severity,
            "damage_type": damage_type,
            "repair_needed": health < 0.7,
        })

    damaged = [f for f in findings if f["repair_needed"]]
    critical = [f for f in findings if f["severity"] == "critical"]

    result = {
        "diagnosis_id": hashlib.sha256(f"diag:{time.time()}".encode()).hexdigest()[:10],
        "modules_scanned": len(MODULES),
        "healthy": len(findings) - len(damaged),
        "degraded": len(damaged),
        "critical": len(critical),
        "findings": findings,
        "timestamp": time.time(),
    }

    log["diagnoses"].append(result)
    log["diagnoses"] = log["diagnoses"][-50:]
    _save(REPAIR_LOG, log)

    return {"action": "diagnose", "result": result}


def repair(module: str = None) -> dict:
    """Initiate repair on a specific module or all damaged modules."""
    log = _load(REPAIR_LOG, {"diagnoses": [], "repairs": []})

    if module:
        targets = [module]
    else:
        # Find most recent damaged modules
        last_diag = log["diagnoses"][-1] if log["diagnoses"] else None
        if last_diag:
            targets = [f["module"] for f in last_diag["findings"] if f["repair_needed"]][:3]
        else:
            targets = random.sample(MODULES, min(2, len(MODULES)))

    repairs = []
    for mod in targets:
        repair_type = random.choice(REPAIR_TYPES)
        success = random.random() > 0.15  # 85% success rate
        repair_result = {
            "module": mod,
            "repair_type": repair_type,
            "success": success,
            "health_before": round(random.uniform(0.3, 0.6), 3),
            "health_after": round(random.uniform(0.7, 1.0), 3) if success else round(random.uniform(0.3, 0.5), 3),
            "resonance_used": round(random.uniform(0.1, 0.5), 3),
            "timestamp": time.time(),
        }
        repairs.append(repair_result)

    log["repairs"].extend(repairs)
    log["repairs"] = log["repairs"][-200:]
    _save(REPAIR_LOG, log)

    return {
        "action": "repair",
        "repairs": repairs,
        "total_repairs": len(log["repairs"]),
        "success_rate": round(sum(1 for r in repairs if r["success"]) / max(len(repairs), 1), 3),
    }


def status() -> dict:
    """Overview of repair network health."""
    log = _load(REPAIR_LOG, {"diagnoses": [], "repairs": []})

    total_repairs = len(log.get("repairs", []))
    successful = sum(1 for r in log.get("repairs", []) if r["success"])
    repair_types = {}
    for r in log.get("repairs", []):
        t = r["repair_type"]
        repair_types[t] = repair_types.get(t, 0) + 1

    return {
        "action": "status",
        "total_diagnoses": len(log.get("diagnoses", [])),
        "total_repairs": total_repairs,
        "successful_repairs": successful,
        "overall_success_rate": round(successful / max(total_repairs, 1), 3),
        "repair_type_distribution": repair_types,
    }


def route(path: str) -> dict:
    if path == "/diagnose":
        return diagnose()
    elif path == "/repair":
        return repair()
    elif path.startswith("/repair/"):
        mod = path.split("/")[-1]
        return repair(mod)
    elif path == "/status":
        return status()
    return {"error": "unknown", "available": ["/diagnose", "/repair", "/repair/{module}", "/status"]}


def handler(payload=None):
    payload = payload or {}
    return route(payload.get("path", "/diagnose"))
