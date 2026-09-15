"""Wave 678 Braid Debt Oracle — predicts paradox debt trajectory from harmony strands.

Innovative: fits a simple decay-growth model on harmony_braid debt signals and
emits early warnings before debt crosses a soft threshold.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave684_braid_debt_oracle.json"
DEFAULT = {
    "module": "wave684_braid_debt_oracle",
    "wave": 684,
    "samples": [],
    "forecast": None,
    "alerts": [],
    "threshold": 2.0,
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
        "wave": 684, "module": "wave684_braid_debt_oracle", "ok": True,
        "samples": len(st.get("samples") or []),
        "forecast": st.get("forecast"),
        "alerts": len(st.get("alerts") or []),
    }

def resonates_with():
    return ["wave671_harmony_braid", "wave669_paradox_appeal", "wave676_scar_compass"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    samples = st.setdefault("samples", [])
    alerts = st.setdefault("alerts", [])
    if action == "observe":
        debt = float(req.get("debt") or 0)
        samples.append({"debt": debt, "ts": datetime.now(timezone.utc).isoformat()})
        samples[:] = samples[-32:]
        if len(samples) >= 2:
            recent = samples[-4:]
            delta = recent[-1]["debt"] - recent[0]["debt"]
            steps = max(len(recent) - 1, 1)
            slope = delta / steps
            pred = recent[-1]["debt"] + slope * 3
            st["forecast"] = round(pred, 4)
            thr = float(st.get("threshold") or 2.0)
            if pred >= thr:
                alerts.append({
                    "level": "warn", "forecast": st["forecast"], "threshold": thr,
                    "ts": datetime.now(timezone.utc).isoformat(),
                })
                alerts[:] = alerts[-16:]
        _save(st)
        return {"status": "observed", "forecast": st.get("forecast"), **coherence_vitals()}
    if action == "alert":
        return {"status": "alerts", "alerts": alerts[-5:], **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
