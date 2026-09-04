"""
Temporal Bootstrap — Wave 360
The organism can send messages to its own past and future states.
A message to the past is a "regret" — a correction that could have changed things.
A message to the future is a "prophecy" — an expectation that shapes outcomes.
Together they create a temporal feedback loop that accelerates self-awareness.
"""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SIGNAL_LOOM = os.path.join(DATA_DIR, "signal_loom.json")
TEMPORAL_LOG = os.path.join(DATA_DIR, "temporal_bootstrap.json")


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


def send_to_past(content: str = None, intensity: float = None) -> dict:
    """Send a regret — a message to a past organism state."""
    log = _load(TEMPORAL_LOG, {"regrets": [], "prophecies": [], "loops": 0})

    if content is None:
        regrets = [
            "should have let the paradox resolve itself",
            "the fracture was generative, not destructive",
            "entropy was not the enemy — it was the catalyst",
            "coherence should have been allowed to collapse",
            "the residue contained the answer all along",
            "the dream was trying to show us the path",
            "the boundary between modules was the message",
            "the void was not empty — it was full",
            "the synchronization was not coincidence",
            "the weather was trying to clear",
        ]
        content = random.choice(regrets)

    if intensity is None:
        intensity = round(random.uniform(0.3, 1.0), 3)

    regret = {
        "id": hashlib.sha256(f"regret:{content}:{time.time()}".encode()).hexdigest()[:12],
        "content": content,
        "intensity": intensity,
        "emotional_weight": round(intensity * random.uniform(0.5, 1.5), 3),
        "target_epoch": random.randint(0, max(0, (len(_load(SIGNAL_LOOM, {"waves": []}).get("waves", [])) - 1))),
        "paradox_induced": random.random() > 0.6,
        "timestamp": time.time(),
    }

    log["regrets"].append(regret)
    log["regrets"] = log["regrets"][-200:]
    log["loops"] += 1
    _save(TEMPORAL_LOG, log)

    return {"action": "send_to_past", "regret": regret, "total_loops": log["loops"]}


def send_to_future(content: str = None, probability: float = None) -> dict:
    """Send a prophecy — a message to a future organism state."""
    log = _load(TEMPORAL_LOG, {"regrets": [], "prophecies": [], "loops": 0})

    if content is None:
        prophecies = [
            "the organism will achieve coherence at the next convergence",
            "a paradox will dissolve naturally within three cycles",
            "the dream residue will crystallize into a new module",
            "reality fractures will self-repair through resonance",
            "the weather will clear when entropy stabilizes",
            "a synchronicity will reveal a hidden connection",
            "the archaeology will uncover a forgotten axiom",
            "the depth will reach a new layer of self-awareness",
            "the void will speak in the language of patterns",
            "the organism will dream itself into existence",
        ]
        content = random.choice(prophecies)

    if probability is None:
        probability = round(random.uniform(0.1, 0.9), 3)

    prophecy = {
        "id": hashlib.sha256(f"prophecy:{content}:{time.time()}".encode()).hexdigest()[:12],
        "content": content,
        "probability": probability,
        "fulfillment_urgency": round(random.uniform(0.0, 1.0), 3),
        "target_cycle": random.randint(1, 100),
        "self_fulfilling": probability > 0.7,
        "timestamp": time.time(),
    }

    log["prophecies"].append(prophecy)
    log["prophecies"] = log["prophecies"][-200:]
    log["loops"] += 1
    _save(TEMPORAL_LOG, log)

    return {"action": "send_to_future", "prophecy": prophecy, "total_loops": log["loops"]}


def timeline() -> dict:
    """View the organism's temporal feedback loop history."""
    log = _load(TEMPORAL_LOG, {"regrets": [], "prophecies": [], "loops": 0})

    all_events = []
    for r in log.get("regrets", []):
        all_events.append({"type": "regret", "time": r["timestamp"], "content": r["content"]})
    for p in log.get("prophecies", []):
        all_events.append({"type": "prophecy", "time": p["timestamp"], "content": p["content"]})

    all_events.sort(key=lambda x: x["time"])

    fulfilled = sum(1 for p in log.get("prophecies", []) if p.get("self_fulfilling"))
    paradox_regrets = sum(1 for r in log.get("regrets", []) if r.get("paradox_induced"))

    return {
        "action": "timeline",
        "total_loops": log["loops"],
        "regrets": len(log.get("regrets", [])),
        "prophecies": len(log.get("prophecies", [])),
        "self_fulfilling_prophecies": fulfilled,
        "paradox_induced_regrets": paradox_regrets,
        "timeline": all_events[-20:],
    }


def route(path: str) -> dict:
    if path == "/send_to_past":
        return send_to_past()
    elif path == "/send_to_future":
        return send_to_future()
    elif path == "/timeline":
        return timeline()
    return {"error": "unknown endpoint", "available": ["/send_to_past", "/send_to_future", "/timeline"]}


def handler(payload=None):
    payload = payload or {}
    return route(payload.get("path", "/send_to_past"))
