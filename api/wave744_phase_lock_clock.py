"""Wave 744 Phase-Lock Clock — organism time is agreement, not wall clock."""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave744_phase_lock_clock.json"
DEFAULT = {"module": "wave744_phase_lock_clock", "wave": 744, "phase": 0.0, "epoch": 0,
           "ticks": [], "epsilon": 0.08, "quorum": 3}


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
    return {"wave": 744, "module": "wave744_phase_lock_clock", "ok": True,
            "phase": st.get("phase", 0), "epoch": st.get("epoch", 0),
            "pending_ticks": len(st.get("ticks") or [])}


def resonates_with():
    return ["wave457_phase_lock", "wave701_still_compound", "wave674_dawn_ledger"]


def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    if action == "tick":
        node = str(req.get("node") or "anon")[:32]
        phase = float(req.get("phase") or 0) % 1.0
        ticks = st.setdefault("ticks", [])
        ticks.append({"node": node, "phase": phase, "ts": datetime.now(timezone.utc).isoformat()})
        st["ticks"] = ticks[-32:]
        _save(st)
        return {"status": "ticked", "phase": phase, **coherence_vitals()}
    if action == "lock":
        ticks = st.get("ticks") or []
        quorum = int(st.get("quorum") or 3)
        eps = float(st.get("epsilon") or 0.08)
        if len(ticks) < quorum:
            return {"status": "no_quorum", "need": quorum, "have": len(ticks), **coherence_vitals()}
        recent = ticks[-quorum:]
        phases = [float(t["phase"]) for t in recent]
        mean = sum(phases) / len(phases)
        if max(abs(p - mean) for p in phases) > eps:
            return {"status": "desync", "spread": round(max(phases) - min(phases), 4), **coherence_vitals()}
        st["phase"] = round(mean, 6)
        st["epoch"] = int(st.get("epoch") or 0) + 1
        st["ticks"] = []
        st["last_lock"] = datetime.now(timezone.utc).isoformat()
        _save(st)
        return {"status": "locked", "phase": st["phase"], "epoch": st["epoch"], **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
