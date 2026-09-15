"""Wave 677 Void Meter — measures productive absence as a first-class resource.

Never-before: tracks deliberate non-actions (skipped routes, silent frames,
deferred features) and scores them as void capital that can fund Quiet Crown
bids or Oblivion listings without minting noise.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave683_void_meter.json"
DEFAULT = {
    "module": "wave683_void_meter",
    "wave": 683,
    "void_capital": 0.0,
    "events": [],
    "spent": 0.0,
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
        "wave": 683, "module": "wave683_void_meter", "ok": True,
        "void_capital": st.get("void_capital", 0),
        "events": len(st.get("events") or []),
        "spent": st.get("spent", 0),
    }

def resonates_with():
    return ["wave672_root_archive", "wave675_consensus_bloom", "wave676_scar_compass"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    events = st.setdefault("events", [])
    if action == "record":
        kind = str(req.get("kind") or "absence")[:32]
        amount = float(req.get("amount") or 1.0)
        label = str(req.get("label") or kind)[:64]
        events.append({
            "kind": kind, "amount": amount, "label": label,
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        events[:] = events[-64:]
        st["void_capital"] = round(float(st.get("void_capital") or 0) + amount, 4)
        _save(st)
        return {"status": "recorded", "void_capital": st["void_capital"], **coherence_vitals()}
    if action == "spend":
        amount = float(req.get("amount") or 0)
        bal = float(st.get("void_capital") or 0)
        if amount > bal:
            return {"status": "insufficient", **coherence_vitals()}
        st["void_capital"] = round(bal - amount, 4)
        st["spent"] = round(float(st.get("spent") or 0) + amount, 4)
        _save(st)
        return {"status": "spent", "amount": amount, **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
