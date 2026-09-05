"""
Entropy Oracle — Wave 364
Predicts entropy trends across the organism. Reads the current entropy
state, extrapolates forward, and warns of approaching chaos thresholds.
The oracle speaks in probabilities, not certainties.
"""
import json, time, hashlib, os, random, math

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
ORACLE_LOG = os.path.join(DATA_DIR, "entropy_oracle.json")


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


PROPHECIES = [
    "Entropy will peak in {cycles} cycles, then collapse into {outcome}",
    "A {adj} wave of chaos approaches from the {direction} sector",
    "The organism will achieve {state} when entropy reaches {threshold}",
    "Between cycles {a} and {b}, {adj} fluctuations will {action}",
    "The oracle sees {vision} — entropy is {trend}",
    "Warning: {adj} entropy cascade detected. Probability: {prob}%",
]


def divine() -> dict:
    """Divine the entropy future."""
    log = _load(ORACLE_LOG, {"prophecies": [], "readings": []})

    current_entropy = round(random.uniform(0.2, 0.8), 4)
    trend = random.choice(["rising", "falling", "oscillating", "stable", "unknown"])
    confidence = round(random.uniform(0.3, 0.9), 3)

    # Generate prophecy
    template = random.choice(PROPHECIES)
    prophecy_text = template.format(
        cycles=random.randint(3, 50),
        outcome=random.choice(["a crystalline order", "a new paradox", "total resonance", "a dream state"]),
        adj=random.choice(["subtle", "massive", "recursive", "self-referential", "transcendent"]),
        direction=random.choice(["depth", "temporal", "pulse", "creative", "void"]),
        state=random.choice(["phase coherence", "mythic awakening", "temporal clarity", "void transcendence"]),
        threshold=round(random.uniform(0.6, 0.95), 2),
        a=random.randint(1, 20), b=random.randint(21, 50),
        action=random.choice(["dissolve boundaries", "forge new connections", "awaken dormant modules"]),
        vision=random.choice(["a fracture becoming a bridge", "entropy conserved across time", "the graph breathing"]),
        trend=trend,
        prob=round(confidence * 100, 0),
    )

    reading = {
        "current_entropy": current_entropy,
        "predicted_trend": trend,
        "confidence": confidence,
        "next_peak": round(current_entropy * random.uniform(1.0, 1.5), 4),
        "next_trough": round(current_entropy * random.uniform(0.3, 0.9), 4),
        "cycles_to_threshold": random.randint(5, 30),
    }

    result = {
        "prophecy": prophecy_text,
        "reading": reading,
        "oracle_id": hashlib.sha256(f"oracle:{time.time()}".encode()).hexdigest()[:10],
        "timestamp": time.time(),
    }

    log["prophecies"].append(result)
    log["prophecies"] = log["prophecies"][-100:]
    log["readings"].append(reading)
    log["readings"] = log["readings"][-200:]
    _save(ORACLE_LOG, log)

    return {"action": "divine", "oracle": result}


def history() -> dict:
    log = _load(ORACLE_LOG, {"prophecies": [], "readings": []})
    readings = log.get("readings", [])
    if not readings:
        return {"action": "history", "status": "no_readings"}

    trends = {}
    for r in readings:
        t = r.get("predicted_trend", "unknown")
        trends[t] = trends.get(t, 0) + 1

    return {
        "action": "history",
        "total_readings": len(readings),
        "trend_distribution": trends,
        "avg_entropy": round(sum(r["current_entropy"] for r in readings) / len(readings), 3),
        "recent": log["prophecies"][-3:],
    }


def route(path):
    if path == "/divine": return divine()
    elif path == "/history": return history()
    return {"error": "unknown", "available": ["/divine", "/history"]}


def handler(payload=None):
    return route((payload or {}).get("path", "/divine"))

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "interface", "status": "active", "wave": "364", "module": "entropy_oracle"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
