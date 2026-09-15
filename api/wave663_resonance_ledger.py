"""Wave 663 — Resonance Ledger.

Economic layer for resonance exchange:
- Mint resonance credits for organs
- Transfer resonance between entities
- Balance and full ledger views
"""
import json, time
from pathlib import Path
STATE = Path("data/wave663_resonance_ledger.json")
def _load():
    if STATE.exists(): return json.loads(STATE.read_text())
    return {"accounts": {}, "transfers": [], "tick": 0}
def _save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True); STATE.write_text(json.dumps(s, indent=2))
def _status():
    s = _load(); return {"ok": True, "tick": s["tick"], "accounts": len(s["accounts"]), "transfers": len(s["transfers"])}
def _mint(account="organ", amount=10.0, reason="resonance"):
    s = _load(); s["tick"] += 1
    acc = s["accounts"].setdefault(account, {"balance": 0.0, "events": 0})
    acc["balance"] = round(acc["balance"] + amount, 4); acc["events"] += 1
    s["transfers"].append({"type": "mint", "to": account, "amount": amount, "reason": reason, "time": time.time()})
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
    s["transfers"].append({"type": "transfer", "from": frm, "to": to, "amount": amount, "reason": reason, "time": time.time()})
    _save(s); return {"ok": True, "from": frm, "to": to, "amount": amount, "balances": {"from": src["balance"], "to": dst["balance"]}}
def _balance(account="organ"):
    s = _load(); acc = s["accounts"].get(account)
    return {"ok": True, "account": account, "balance": acc["balance"] if acc else 0.0}
def _ledger():
    s = _load(); return {"ok": True, "transfers": s["transfers"][-20:], "accounts": {k: v["balance"] for k, v in s["accounts"].items()}}
def handler(req):
    action = req.get("action", "status")
    if action == "status": return _status()
    elif action == "mint": return _mint(req.get("account", "organ"), req.get("amount", 10.0), req.get("reason", "resonance"))
    elif action == "transfer": return _transfer(req.get("from", "a"), req.get("to", "b"), req.get("amount", 1.0), req.get("reason", "exchange"))
    elif action == "balance": return _balance(req.get("account", "organ"))
    elif action == "ledger": return _ledger()
    return {"ok": False, "error": f"Unknown action: {action}"}
def coherence_vitals():
    s = _load(); return {"wave": 663, "accounts": len(s["accounts"]), "transfers": len(s["transfers"])}
def resonates_with(): return ["wave665_mycelial_network", "wave662_dream_compiler", "wave652_economy_unifier"]
