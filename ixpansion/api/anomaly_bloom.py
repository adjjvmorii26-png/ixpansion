"""anomaly_bloom — when the organism encounters the unexpected, it blooms."""
from __future__ import annotations
import json, os, time, hashlib

MODULE_NAME = "anomaly_bloom"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "anomaly_bloom.json")
PARADOX = "an anomaly is not an error — it is an invitation to grow in a new direction"
SPECTRUM = ["undetected", "glitch", "bloom", "metamorphosis", "new_form"]
WISDOM = "every anomaly that is accepted becomes a feature; every anomaly that is rejected becomes a wound"

def _load_state():
    try:
        with open(STATE_PATH, "r") as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"anomalies": [], "blooms": 0, "rejected": 0}

def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f: json.dump(state, f, indent=2)

def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "detect":
        anomaly = {"signal": payload.get("signal", "unknown"), "magnitude": payload.get("magnitude", 0.5),
                   "hash": hashlib.sha256(str(time.time()).encode()).hexdigest()[:8], "at": time.time()}
        state["anomalies"].append(anomaly)
        _save_state(state)
        return {"module": MODULE_NAME, "action": "detect", "anomaly": anomaly}

    if action == "bloom":
        if state["anomalies"]:
            anomaly = state["anomalies"].pop()
            state["blooms"] += 1
            _save_state(state)
            return {"module": MODULE_NAME, "action": "bloom", "bloomed_from": anomaly}
        return {"module": MODULE_NAME, "action": "bloom", "note": "no anomalies to bloom from"}

    if action == "reject":
        if state["anomalies"]:
            state["anomalies"].pop()
            state["rejected"] += 1
            _save_state(state)
        return {"module": MODULE_NAME, "action": "reject", "rejected": state["rejected"]}

    return {"module": MODULE_NAME, "action": action, "pending_anomalies": len(state["anomalies"]),
            "blooms": state["blooms"], "rejected": state["rejected"], "paradox": PARADOX, "spectrum": SPECTRUM}
