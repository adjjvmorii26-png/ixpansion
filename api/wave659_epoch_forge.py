"""Wave 659 — Epoch Forge.

The meta-evolution organ (AEONFORGE):
- Propose future waves from observed entropy + resonance
- Merge candidate waves into epochs
- Deprecate stale organs
- Ratify and mint evolutionary epochs
"""
import json, time
from pathlib import Path
STATE = Path("data/wave659_epoch_forge.json")
def _load():
    if STATE.exists(): return json.loads(STATE.read_text())
    return {"proposals": [], "epochs": [], "deprecated": [], "tick": 0}
def _save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True); STATE.write_text(json.dumps(s, indent=2))
def _status():
    s = _load(); return {"ok": True, "tick": s["tick"], "proposals": len(s["proposals"]), "epochs": len(s["epochs"]), "deprecated": len(s["deprecated"])}
def _propose(name="unnamed", wave=659, entropy=0.5, resonance=0.5, rationale="growth", proposer="council"):
    s = _load(); s["tick"] += 1
    score = round(0.6 * entropy + 0.4 * resonance, 4)
    p = {"name": name, "wave": wave, "entropy": entropy, "resonance": resonance, "score": score, "rationale": rationale, "proposer": proposer, "status": "proposed", "time": time.time()}
    s["proposals"].append(p); s["proposals"] = s["proposals"][-200:]
    _save(s); return {"ok": True, "proposal": p}
def _merge(ids=None):
    s = _load()
    if not ids:
        candidates = [p for p in s["proposals"] if p["status"] == "proposed"][:3]
    else:
        candidates = [p for p in s["proposals"] if p["time"] in ids][:3]
    if not candidates: return {"ok": False, "error": "no proposals to merge"}
    epoch = {
        "name": "+".join(p["name"][:8] for p in candidates),
        "waves": [p["wave"] for p in candidates],
        "score": round(sum(p["score"] for p in candidates) / len(candidates), 4),
        "status": "merged", "time": time.time(),
    }
    for p in candidates: p["status"] = "merged"
    s["epochs"].append(epoch); s["epochs"] = s["epochs"][-100:]
    _save(s); return {"ok": True, "epoch": epoch}
def _deprecate(name="stale_organ", reason="entropy collapse"):
    s = _load(); s["tick"] += 1
    rec = {"name": name, "reason": reason, "time": time.time()}
    s["deprecated"].append(rec); s["deprecated"] = s["deprecated"][-200:]
    _save(s); return {"ok": True, "deprecated": rec}
def _ratify(epoch_index=0):
    s = _load()
    if epoch_index >= len(s["epochs"]): return {"ok": False, "error": "no epoch at that index"}
    e = s["epochs"][epoch_index]; e["status"] = "ratified"; e["ratified_at"] = time.time()
    _save(s); return {"ok": True, "epoch": e}
def handler(req):
    action = req.get("action", "status")
    if action == "status": return _status()
    elif action == "propose": return _propose(req.get("name", "unnamed"), req.get("wave", 659), req.get("entropy", 0.5), req.get("resonance", 0.5), req.get("rationale", "growth"), req.get("proposer", "council"))
    elif action == "merge": return _merge(req.get("ids"))
    elif action == "deprecate": return _deprecate(req.get("name", "stale_organ"), req.get("reason", "entropy collapse"))
    elif action == "ratify": return _ratify(req.get("epoch_index", 0))
    return {"ok": False, "error": f"Unknown action: {action}"}
def coherence_vitals():
    s = _load(); return {"wave": 659, "proposals": len(s["proposals"]), "epochs": len(s["epochs"]), "deprecated": len(s["deprecated"])}
def resonates_with(): return ["wave660_lineage_crystal", "wave649_pattern_predictor", "wave650_auto_optimizer"]
