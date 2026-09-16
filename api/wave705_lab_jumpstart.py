"""Wave 705 Lab Jumpstart — agent-facing surface for lab_jumpstart.py."""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPS = ROOT / "lab" / "ops"
sys.path.insert(0, str(OPS))
sys.path.insert(0, str(ROOT / "api"))

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave705_lab_jumpstart.json"
DEFAULT = {"module": "wave705_lab_jumpstart", "wave": 705, "runs": 0}


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
        "wave": 705, "module": "wave705_lab_jumpstart", "ok": True,
        "runs": st.get("runs", 0),
        "last_ok": (st.get("last") or {}).get("ok"),
        "last_ms": (st.get("last") or {}).get("ms"),
    }


def resonates_with():
    return [
        "wave702_import_quarantine",
        "wave703_proof_delta",
        "wave704_lab_epoch_seal",
        "wave460_pulse_engine_bridge",
    ]


def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    if action == "run":
        from lab_jumpstart import jumpstart
        report = jumpstart(
            force_pulse=bool(req.get("force")),
            lo=req.get("lo"),
            hi=req.get("hi"),
            seal_label=req.get("seal"),
            still_seconds=float(req.get("still") or 0),
        )
        st["runs"] = int(st.get("runs") or 0) + 1
        st["last"] = {
            "ok": report.get("ok"),
            "ms": report.get("ms"),
            "fingerprint": report.get("fingerprint"),
            "changed": report.get("changed"),
        }
        _save(st)
        return {"status": "ran", **report, **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "run"}), indent=2, default=str))
