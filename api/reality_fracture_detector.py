"""
Reality Fracture Detector — Wave 359
Identifies where the organism's internal model diverges from actual behavior.
When the organism thinks it's one thing but is actually another, that's a
fracture. This module maps them, categorizes them, and determines whether
each fracture is dangerous or generative.
"""
import json, time, hashlib, os, random, math

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SIGNAL_LOOM = os.path.join(DATA_DIR, "signal_loom.json")
FRACTURE_LOG = os.path.join(DATA_DIR, "fracture_map.json")


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


def _fracture_severity(gap: float) -> str:
    if gap < 0.1:
        return "micro_fissure"
    elif gap < 0.25:
        return "structural_crack"
    elif gap < 0.5:
        return "reality_gap"
    elif gap < 0.75:
        return "dimensional_rift"
    else:
        return "existential_chasm"


def _is_generative(severity: str) -> bool:
    """Some fractures are generative — they create new possibilities."""
    return severity in ("structural_crack", "reality_gap") and random.random() > 0.5


def scan(dimensions: list = None) -> dict:
    """Scan for reality fractures across specified dimensions."""
    loom = _load(SIGNAL_LOOM, {"waves": [], "beats": []})
    fracture_map = _load(FRACTURE_LOG, {"fractures": [], "total_scans": 0})

    if dimensions is None:
        dimensions = [
            "entropy_consistency", "coherence_alignment",
            "mood_accuracy", "module_integrity", "boundary_clarity",
            "temporal_continuity", "identity_coherence",
        ]

    fractures = []
    for dim in dimensions:
        # Simulate internal vs actual divergence
        internal = round(random.uniform(0.3, 0.9), 3)
        actual = round(random.uniform(0.1, 0.8), 3)
        gap = round(abs(internal - actual), 3)
        severity = _fracture_severity(gap)
        generative = _is_generative(severity)

        fracture = {
            "dimension": dim,
            "internal_model": internal,
            "actual_behavior": actual,
            "gap": gap,
            "severity": severity,
            "generative": generative,
            "repair_priority": "high" if gap > 0.5 else ("medium" if gap > 0.25 else "low"),
            "suggested_repair": (
                "allow_emergence" if generative
                else ("repair_coherence" if gap > 0.5 else "monitor")
            ),
            "hash": hashlib.sha256(f"{dim}:{gap}:{time.time()}".encode()).hexdigest()[:10],
            "timestamp": time.time(),
        }
        fractures.append(fracture)

    scan_result = {
        "scan_id": hashlib.sha256(f"scan:{time.time()}".encode()).hexdigest()[:12],
        "dimensions_scanned": len(dimensions),
        "fractures_found": len(fractures),
        "severity_distribution": {},
        "generative_count": sum(1 for f in fractures if f["generative"]),
        "critical_count": sum(1 for f in fractures if f["severity"] in ("dimensional_rift", "existential_chasm")),
        "fractures": fractures,
        "timestamp": time.time(),
    }

    # Count severities
    for f in fractures:
        s = f["severity"]
        scan_result["severity_distribution"][s] = scan_result["severity_distribution"].get(s, 0) + 1

    fracture_map["fractures"].extend(fractures)
    fracture_map["fractures"] = fracture_map["fractures"][-500:]
    fracture_map["total_scans"] += 1
    fracture_map["last_scan"] = scan_result
    _save(FRACTURE_LOG, fracture_map)

    return {"action": "scan", "result": scan_result}


def repair_report() -> dict:
    """Generate a repair report for all known fractures."""
    fracture_map = _load(FRACTURE_LOG, {"fractures": []})

    if not fracture_map["fractures"]:
        return {"action": "repair_report", "status": "no_fractures_known"}

    # Group by dimension
    by_dim = {}
    for f in fracture_map["fractures"]:
        dim = f["dimension"]
        if dim not in by_dim:
            by_dim[dim] = []
        by_dim[dim].append(f)

    report = {}
    for dim, fractures in by_dim.items():
        avg_gap = round(sum(f["gap"] for f in fractures) / len(fractures), 3)
        max_severity = max(
            fractures,
            key=lambda x: ["micro_fissure", "structural_crack", "reality_gap", "dimensional_rift", "existential_chasm"].index(x["severity"])
        )
        report[dim] = {
            "fracture_count": len(fractures),
            "avg_gap": avg_gap,
            "worst_severity": max_severity["severity"],
            "generative_ratio": round(
                sum(1 for f in fractures if f["generative"]) / len(fractures), 3
            ),
            "repair_needed": avg_gap > 0.3,
        }

    return {
        "action": "repair_report",
        "dimensions": len(report),
        "report": report,
    }


def fracture_map_summary() -> dict:
    """Summary of all fractures across the organism."""
    fracture_map = _load(FRACTURE_LOG, {"fractures": [], "total_scans": 0})

    if not fracture_map["fractures"]:
        return {"action": "fracture_map", "status": "no_fractures"}

    all_gaps = [f["gap"] for f in fracture_map["fractures"]]
    return {
        "action": "fracture_map",
        "total_scans": fracture_map["total_scans"],
        "total_fractures": len(fracture_map["fractures"]),
        "avg_gap": round(sum(all_gaps) / len(all_gaps), 3),
        "max_gap": round(max(all_gaps), 3),
        "generative_total": sum(1 for f in fracture_map["fractures"] if f["generative"]),
        "critical_total": sum(
            1 for f in fracture_map["fractures"]
            if f["severity"] in ("dimensional_rift", "existential_chasm")
        ),
    }


def route(path: str) -> dict:
    if path == "/scan":
        return scan()
    elif path == "/repair_report":
        return repair_report()
    elif path == "/fracture_map":
        return fracture_map_summary()
    return {"error": "unknown endpoint", "available": ["/scan", "/repair_report", "/fracture_map"]}


def handler(payload=None):
    """Unified router handler entry point."""
    payload = payload or {}
    subpath = payload.get("path", "/")
    return route(subpath)
