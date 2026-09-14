"""Wave 648 — Ambient Sensor.

Background sensing, always-on awareness:
- Signal channels (each channel has a rolling buffer)
- Sense ticks that decay over time
- Channel aggregation and summary
"""
import json, time
from pathlib import Path
STATE = Path("data/wave648_ambient_sensor.json")
def _load():
    if STATE.exists(): return json.loads(STATE.read_text())
    return {"channels": {}, "signals": [], "tick": 0}
def _save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True); STATE.write_text(json.dumps(s, indent=2))
def _status():
    s = _load(); return {"ok": True, "tick": s["tick"], "channels": len(s["channels"]), "signals": len(s["signals"])}
def _sense(channel="default", value=1.0, source="organism"):
    s = _load(); s["tick"] += 1
    sig = {"channel": channel, "value": value, "source": source, "time": time.time()}
    s["signals"].append(sig); s["signals"] = s["signals"][-1000:]
    ch = s["channels"].setdefault(channel, {"signals": 0, "sum": 0.0})
    ch["signals"] += 1; ch["sum"] += value
    _save(s); return {"ok": True, "signal": sig}
def _channel(channel="default"):
    s = _load(); ch = s["channels"].get(channel)
    if not ch: return {"ok": True, "channel": channel, "signals": 0, "mean": 0.0}
    return {"ok": True, "channel": channel, "signals": ch["signals"], "mean": round(ch["sum"] / ch["signals"], 4)}
def _summary():
    s = _load(); now = time.time()
    fresh = [x for x in s["signals"] if now - x["time"] < 300]
    decayed = len(s["signals"]) - len(fresh)
    return {"ok": True, "fresh": len(fresh), "decayed": decayed, "channels": {k: v["signals"] for k, v in s["channels"].items()}}
def handler(req):
    action = req.get("action", "status")
    if action == "status": return _status()
    elif action == "sense": return _sense(req.get("channel", "default"), req.get("value", 1.0), req.get("source", "organism"))
    elif action == "channel": return _channel(req.get("channel", "default"))
    elif action == "summary": return _summary()
    return {"ok": False, "error": f"Unknown action: {action}"}
def coherence_vitals():
    s = _load(); return {"wave": 648, "channels": len(s["channels"]), "signals": len(s["signals"])}
def resonates_with(): return ["wave649_pattern_predictor", "wave634_temporal_field", "wave644_self_model"]
