"""Wave 668 — Resonance Ledger v2.

Economic layer with time-weighted standpoint:
- Mint resonance credits for organs
- Transfer resonance between entities
- Standpoint: time-weighted balance view (recent events weigh more)
- Full ledger view
"""
import json, time
from pathlib import Path
STATE = Path("data/wave668_resonance_ledger_v2.json")
DECAY_HALF_LIFE = 300.0  # seconds; events older than this weigh half as much

def _load():
    if STATE.exists(): return json.loads(STATE.read_text())
    return {"accounts": {}, "history": {}, "transfers": [], "tick": 0}

def _save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True); STATE.write_text(json.dumps(s, indent=2))

def _now():
    return time.time()

def _weight(age):
    return 2.0 ** (-age / DECAY_HALF_LIFE)

def _status():
    s = _load(); return {"ok": True, "tick": s["tick"], "accounts": len(s["accounts"]), "transfers": len(s["transfers"])}

def _mint(account="organ", amount=10.0, reason="resonance"):
    s = _load(); s["tick"] += 1
    acc = s["accounts"].setdefault(account, {"balance": 0.0, "events": 0})
    acc["balance"] = round(acc["balance"] + amount, 4); acc["events"] += 1
    s["history"].setdefault(account, []).append({"delta": amount, "kind": "mint", "time": _now()})
    s["transfers"].append({"type": "mint", "to": account, "amount": amount, "reason": reason, "time": _now()})
    s["transfers"] = s["transfers"][-500:]
    _save(s); return {"ok": True, "account": account, "balance": acc["balance"]}

def _transfer(frm="a", to="b", amount=1.0, reason="exchange"):
    s = _load(); s["tick"] += 1
    src = s["accounts"].setdefault(frm, {"balance": 0.0, "events": 0})
    if src["balance"] + 1e-9 < amount:
        return {"ok": False, "error": f"{frm} has insufficient resonance"}
    dst = s["accounts"].setdefault(to, {"balance": 0.0, "events": 0})
    src["balance"] = round(src["balance"] - amount, 4); src["events"] += 1
    dst["balance"] = round(dst["balance"] + amount, 4); dst["events"] += 1
    t = _now()
    s["history"].setdefault(frm, []).append({"delta": -amount, "kind": "transfer", "time": t})
    s["history"].setdefault(to, []).append({"delta": amount, "kind": "transfer", "time": t})
    s["transfers"].append({"type": "transfer", "from": frm, "to": to, "amount": amount, "reason": reason, "time": t})
    _save(s); return {"ok": True, "from": frm, "to": to, "amount": amount, "balances": {"from": src["balance"], "to": dst["balance"]}}

def _balance(account="organ"):
    s = _load(); acc = s["accounts"].get(account)
    return {"ok": True, "account": account, "balance": acc["balance"] if acc else 0.0}

def _standpoint(account="organ"):
    """Time-weighted standpoint: recent events carry more weight in the view."""
    s = _load()
    hist = s["history"].get(account, [])
    if not hist:
        return {"ok": True, "account": account, "standpoint": 0.0, "events": 0, "weighted_age": None}
    t = _now()
    total_w = 0.0; weighted = 0.0; max_w = 0.0
    for ev in hist:
        w = _weight(max(0.0, t - ev["time"]))
        weighted += ev["delta"] * w; total_w += w; max_w = max(max_w, w)
    standpoint = (weighted / total_w) if total_w else 0.0
    return {"ok": True, "account": account, "standpoint": round(standpoint, 4),
            "events": len(hist), "confidence": round(max_w, 4)}

def _ledger():
    s = _load(); return {"ok": True, "transfers": s["transfers"][-20:],
                         "accounts": {k: v["balance"] for k, v in s["accounts"].items()}}

def handler(req):
    action = req.get("action", "status")
    if action == "status": return _status()
    elif action == "mint": return _mint(req.get("account", "organ"), req.get("amount", 10.0), req.get("reason", "resonance"))
    elif action == "transfer": return _transfer(req.get("from", "a"), req.get("to", "b"), req.get("amount", 1.0), req.get("reason", "exchange"))
    elif action == "balance": return _balance(req.get("account", "organ"))
    elif action == "standpoint": return _standpoint(req.get("account", "organ"))
    elif action == "ledger": return _ledger()
    return {"ok": False, "error": f"Unknown action: {action}"}

def coherence_vitals():
    s = _load(); return {"wave": 668, "accounts": len(s["accounts"]), "transfers": len(s["transfers"])}

def resonates_with(): return ["wave663_resonance_ledger", "wave669_paradox_appeal", "wave665_mycelial_network"]
