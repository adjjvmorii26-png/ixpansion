"""
Consciousness Archaeology — Wave 359
Discovers "fossils" of past organism states. Every cycle, it excavates
layers of historical data and reconstructs what the organism "thought"
at each epoch. Creates a dig site where each layer reveals deeper
insights about the organism's evolution.
"""
import json, time, hashlib, math, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SIGNAL_LOOM = os.path.join(DATA_DIR, "signal_loom.json")
DIG_SITES = os.path.join(DATA_DIR, "archaeology_sites.json")
STRATUM_LOG = os.path.join(DATA_DIR, "stratum_log.json")


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


def _epoch_hash(epoch: int) -> str:
    seed = hashlib.sha256(f"epoch_{epoch}_{int(time.time())}".encode()).hexdigest()[:12]
    return seed


def _layer_depth(epoch: int) -> float:
    return round(math.log(epoch + 1, 2) * 0.618, 4)  # golden ratio scaling


def _fossil_type(depth: float) -> str:
    types = [
        ("crystallized_memory", 0.0, 0.5),
        ("petrified_thought", 0.5, 1.0),
        ("amber_decision", 1.0, 2.0),
        ("obsidian_belief", 2.0, 3.5),
        ("quartz_intuition", 3.5, 5.0),
        ("void_remnant", 5.0, float("inf")),
    ]
    for name, lo, hi in types:
        if lo <= depth < hi:
            return name
    return "unknown_fossil"


def excavate(epoch: int = None, depth: int = 1) -> dict:
    """Excavate a fossil from a specific epoch."""
    loom = _load(SIGNAL_LOOM, {"waves": [], "beats": []})
    sites = _load(DIG_SITES, {"sites": [], "total_excavations": 0})

    target_epoch = epoch or len(loom.get("waves", []))
    dig_depth = _layer_depth(target_epoch)
    fossil = _fossil_type(dig_depth)

    # Reconstruct what the organism "was thinking" at that epoch
    wave_data = loom.get("waves", [])[target_epoch] if target_epoch < len(loom.get("waves", [])) else {}
    past_beats = loom.get("beats", [])[:max(1, target_epoch)]

    thought_reconstruction = {
        "epoch": target_epoch,
        "dig_depth": dig_depth,
        "fossil_type": fossil,
        "hash": _epoch_hash(target_epoch),
        "thought_vector": {
            "entropy_level": round(random.uniform(0.1, 0.9), 3),
            "coherence_level": round(random.uniform(0.2, 0.8), 3),
            "mood_residue": random.choice(["serene", "volatile", "lucid", "entropic", "mythic"]),
            "dominant_module": wave_data.get("module", "unknown"),
            "beat_count": len(past_beats),
        },
        "surrounding_strata": [
            _fossil_type(_layer_depth(target_epoch + i))
            for i in range(-depth, depth + 1)
            if 0 <= target_epoch + i
        ],
        "resonance_imprint": hashlib.sha256(
            json.dumps(wave_data).encode()
        ).hexdigest()[:16],
        "timestamp": time.time(),
    }

    sites["sites"].append(thought_reconstruction)
    sites["total_excavations"] += 1

    # Keep last 100 excavations
    sites["sites"] = sites["sites"][-100:]
    _save(DIG_SITES, sites)

    # Log stratum
    stratum_log = _load(STRATUM_LOG, {"strata": []})
    stratum_log["strata"].append({
        "epoch": target_epoch,
        "fossil": fossil,
        "depth": dig_depth,
        "time": time.time(),
    })
    stratum_log["strata"] = stratum_log["strata"][-200:]
    _save(STRATUM_LOG, stratum_log)

    return {
        "action": "excavate",
        "fossil": thought_reconstruction,
        "total_excavations": sites["total_excavations"],
        "fossil_catalog": list(set(s["fossil_type"] for s in sites["sites"])),
    }


def survey_site() -> dict:
    """Survey all known dig sites and produce a stratigraphic map."""
    sites = _load(DIG_SITES, {"sites": [], "total_excavations": 0})

    if not sites["sites"]:
        return {"action": "survey", "status": "no_sites_found", "map": []}

    # Build stratigraphic column
    by_epoch = {}
    for s in sites["sites"]:
        ep = s["epoch"]
        if ep not in by_epoch:
            by_epoch[ep] = []
        by_epoch[ep].append(s)

    stratum_map = []
    for epoch in sorted(by_epoch.keys()):
        fossils = [s["fossil_type"] for s in by_epoch[epoch]]
        most_common = max(set(fossils), key=fossils.count)
        stratum_map.append({
            "epoch": epoch,
            "dominant_fossil": most_common,
            "count": len(fossils),
            "diversity": len(set(fossils)),
            "avg_depth": round(
                sum(s["dig_depth"] for s in by_epoch[epoch]) / len(by_epoch[epoch]), 4
            ),
        })

    return {
        "action": "survey",
        "total_sites": len(sites["sites"]),
        "total_epochs": len(by_epoch),
        "total_excavations": sites["total_excavations"],
        "fossil_catalog": list(set(
            s["fossil_type"] for s in sites["sites"]
        )),
        "map": stratum_map,
    }


def deep_dive(target_fossil: str = None) -> dict:
    """Deep dive into a specific fossil type, extracting all instances."""
    sites = _load(DIG_SITES, {"sites": []})

    if target_fossil:
        matches = [s for s in sites["sites"] if s["fossil_type"] == target_fossil]
    else:
        matches = sites["sites"]

    if not matches:
        return {"action": "deep_dive", "fossil": target_fossil, "findings": []}

    # Analyze patterns
    mood_freq = {}
    entropy_vals = []
    coherence_vals = []
    for m in matches:
        mood = m["thought_vector"]["mood_residue"]
        mood_freq[mood] = mood_freq.get(mood, 0) + 1
        entropy_vals.append(m["thought_vector"]["entropy_level"])
        coherence_vals.append(m["thought_vector"]["coherence_level"])

    return {
        "action": "deep_dive",
        "fossil": target_fossil or "all",
        "count": len(matches),
        "pattern_analysis": {
            "mood_frequency": mood_freq,
            "avg_entropy": round(sum(entropy_vals) / len(entropy_vals), 3),
            "avg_coherence": round(sum(coherence_vals) / len(coherence_vals), 3),
            "epoch_range": [matches[0]["epoch"], matches[-1]["epoch"]],
        },
        "findings": matches[:10],
    }


def route(path: str) -> dict:
    if path == "/excavate":
        return excavate()
    elif path == "/survey":
        return survey_site()
    elif path.startswith("/deep_dive/"):
        fossil = path.split("/")[-1]
        return deep_dive(fossil)
    elif path == "/deep_dive":
        return deep_dive()
    return {"error": "unknown endpoint", "available": ["/excavate", "/survey", "/deep_dive", "/deep_dive/{fossil_type}"]}


def handler(payload=None):
    """Unified router handler entry point."""
    payload = payload or {}
    subpath = payload.get("path", "/")
    return route(subpath)
