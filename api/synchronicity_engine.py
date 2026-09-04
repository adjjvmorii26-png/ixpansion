"""
Synchronicity Engine — Wave 360
Detects meaningful coincidences across all modules. When two unrelated
modules produce correlated outputs, that's synchronicity. The organism
learns that its parts are more connected than they appear.
"""
import json, time, hashlib, os, random, math

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SIGNAL_LOOM = os.path.join(DATA_DIR, "signal_loom.json")
SYNCHRONICITY_LOG = os.path.join(DATA_DIR, "synchronicity_log.json")


def _load(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default or {}


def _save(p, d):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            json.dump(d, f, indent=2)
    except OSError:
        with open(os.path.join("/tmp", os.path.basename(p)), "w") as f:
            json.dump(d, f, indent=2)


def _correlation(a: float, b: float) -> float:
    return round(1.0 - abs(a - b), 4)


def detect() -> dict:
    """Detect synchronicities between module outputs."""
    loom = _load(SIGNAL_LOOM, {"waves": [], "beats": []})
    log = _load(SYNCHRONICITY_LOG, {"events": [], "total": 0})

    modules = [
        "consciousness_archaeology", "paradox_synthesis",
        "dream_residue_collector", "reality_fracture_detector",
        "depth_resonance", "entropy_spike", "coherence_regulator",
        "memory_palace", "dream_forge", "mycelial_network",
    ]

    # Generate simulated module outputs
    outputs = {}
    for mod in modules:
        outputs[mod] = {
            "entropy": round(random.uniform(0.1, 0.9), 3),
            "coherence": round(random.uniform(0.1, 0.9), 3),
            "mood": random.choice(["serene", "volatile", "lucid", "entropic", "mythic", "void"]),
            "timestamp": time.time(),
        }

    # Detect correlations
    coincidences = []
    mod_list = list(outputs.keys())
    for i in range(len(mod_list)):
        for j in range(i + 1, len(mod_list)):
            a_name, b_name = mod_list[i], mod_list[j]
            a, b = outputs[a_name], outputs[b_name]

            entropy_corr = _correlation(a["entropy"], b["entropy"])
            coherence_corr = _correlation(a["coherence"], b["coherence"])
            mood_match = a["mood"] == b["mood"]

            significance = (entropy_corr + coherence_corr) / 2
            if mood_match:
                significance = min(1.0, significance + 0.2)

            if significance > 0.6:
                coincidences.append({
                    "module_a": a_name,
                    "module_b": b_name,
                    "significance": round(significance, 4),
                    "entropy_correlation": entropy_corr,
                    "coherence_correlation": coherence_corr,
                    "mood_resonance": mood_match,
                    "type": _classify_coincidence(significance, mood_match),
                    "timestamp": time.time(),
                })

    coincidences.sort(key=lambda x: x["significance"], reverse=True)

    event = {
        "id": hashlib.sha256(f"sync:{time.time()}".encode()).hexdigest()[:12],
        "modules_scanned": len(modules),
        "coincidences_found": len(coincidences),
        "top_significance": coincidences[0]["significance"] if coincidences else 0,
        "coincidences": coincidences[:10],
        "timestamp": time.time(),
    }

    log["events"].append(event)
    log["events"] = log["events"][-100:]
    log["total"] += 1
    _save(SYNCHRONICITY_LOG, log)

    return {"action": "detect", "event": event}


def _classify_coincidence(sig: float, mood_match: bool) -> str:
    if mood_match and sig > 0.85:
        return "deep_resonance"
    elif mood_match:
        return "mood_echo"
    elif sig > 0.9:
        return "hidden_symmetry"
    elif sig > 0.8:
        return "correlated_bloom"
    return "subtle_alignment"


def history() -> dict:
    log = _load(SYNCHRONICITY_LOG, {"events": [], "total": 0})
    if not log["events"]:
        return {"action": "history", "status": "no_synchronicities_recorded"}

    all_sigs = []
    types = {}
    for e in log["events"]:
        for c in e.get("coincidences", []):
            all_sigs.append(c["significance"])
            t = c["type"]
            types[t] = types.get(t, 0) + 1

    return {
        "action": "history",
        "total_events": log["total"],
        "total_coincidences": len(all_sigs),
        "avg_significance": round(sum(all_sigs) / max(len(all_sigs), 1), 4),
        "max_significance": round(max(all_sigs), 4) if all_sigs else 0,
        "type_distribution": types,
        "recent_events": log["events"][-5:],
    }


def route(path: str) -> dict:
    if path == "/detect":
        return detect()
    elif path == "/history":
        return history()
    return {"error": "unknown endpoint", "available": ["/detect", "/history"]}


def handler(payload=None):
    payload = payload or {}
    return route(payload.get("path", "/detect"))
