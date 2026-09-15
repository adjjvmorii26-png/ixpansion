"""Wave 456 Echo Budget — finite allowance for recursive self-reference.

Experimental: each organ may echo prior waves only within a budget.
Over-echo soft-throttles narrative loops so the organism stays novel.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave456_echo_budget.json"
DEFAULT = {
    "module": "wave456_echo_budget",
    "wave": 456,
    "budget": 8.0,
    "spent": 0.0,
    "echoes": [],
}

def _load():
    if STATE_FILE.exists():
        try: return json.loads(STATE_FILE.read_text())
        except Exception: pass
    return dict(DEFAULT)

def _save(st):
    DATA.mkdir(parents=True, exist_ok=True)
    try:
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(st, indent=2) + "\n")
        tmp.replace(STATE_FILE)
    except OSError:
        try: STATE_FILE.write_text(json.dumps(st, indent=2) + "\n")
        except OSError: pass

def coherence_vitals():
    st = _load()
    return {
        "wave": 456, "module": "wave456_echo_budget", "ok": True,
        "budget": st.get("budget", 8), "spent": st.get("spent", 0),
        "remaining": round(float(st.get("budget", 8)) - float(st.get("spent", 0)), 4),
    }

def resonates_with():
    return ["wave454_caption_genome", "wave451_proof_tide_amplifier", "wave672_root_archive"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    echoes = st.setdefault("echoes", [])
    if action == "echo":
        target = str(req.get("target") or req.get("wave") or "")[:64]
        cost = float(req.get("cost") or 1.0)
        rem = float(st.get("budget", 8)) - float(st.get("spent", 0))
        if cost > rem:
            return {"status": "throttled", "remaining": round(rem, 4), **coherence_vitals()}
        st["spent"] = round(float(st.get("spent", 0)) + cost, 4)
        echoes.append({
            "target": target, "cost": cost,
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        echoes[:] = echoes[-32:]
        _save(st)
        return {"status": "echoed", "target": target, **coherence_vitals()}
    if action == "refill":
        amount = float(req.get("amount") or 2.0)
        st["budget"] = round(float(st.get("budget", 8)) + amount, 4)
        _save(st)
        return {"status": "refilled", **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
