"""Wave 675 Resonance Timeweight — pure time-decay kernel for Resonance Ledger v2.

Standalone EMA/half-life applicator so any organ can time-weight events without
depending on ledger internals.
"""
from __future__ import annotations
import json, math
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave675_resonance_timeweight.json"
DEFAULT = {"module": "wave675_resonance_timeweight", "wave": 675, "events": [], "half_life": 8.0}

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
    return {"wave": 675, "module": "wave675_resonance_timeweight", "ok": True,
            "events": len(st.get("events") or []), "half_life": st.get("half_life", 8.0)}

def resonates_with():
    return ["wave668_resonance_ledger_v2", "wave663_resonance_ledger", "wave451_proof_tide_amplifier"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    events = st.setdefault("events", [])
    if action == "record":
        amount = float(req.get("amount") or 1.0)
        label = str(req.get("label") or "pulse")[:48]
        events.append({"label": label, "amount": amount, "age": 0,
                       "ts": datetime.now(timezone.utc).isoformat()})
        events[:] = events[-96:]
        _save(st)
        return {"status": "recorded", **coherence_vitals()}
    if action == "decay":
        hl = float(req.get("half_life") or st.get("half_life") or 8.0)
        st["half_life"] = hl
        factor = 0.5 ** (1.0 / max(hl, 0.5))
        for e in events:
            e["age"] = int(e.get("age") or 0) + 1
            e["weight"] = round(float(e.get("amount") or 1) * (factor ** e["age"]), 6)
        events[:] = [e for e in events if e.get("weight", 0) > 0.01]
        _save(st)
        total = sum(e.get("weight", 0) for e in events)
        return {"status": "decayed", "weighted_total": round(total, 4), **coherence_vitals()}
    if action == "balance":
        total = sum(e.get("weight", e.get("amount", 0)) for e in events)
        return {"status": "balance", "total": round(total, 4), "n": len(events), **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
