"""Wave 706 Lab OS Boot — agent surface for lab_os_boot."""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lab" / "ops"))
sys.path.insert(0, str(ROOT / "api"))

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave706_lab_os_boot.json"
DEFAULT = {"module": "wave706_lab_os_boot", "wave": 706, "boots": 0}


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
    last = st.get("last") or {}
    return {
        "wave": 706, "module": "wave706_lab_os_boot", "ok": True,
        "boots": st.get("boots", 0),
        "last_ok": last.get("ok"),
        "last_ms": last.get("ms"),
    }


def resonates_with():
    return ["wave705_lab_jumpstart", "wave702_import_quarantine", "wave460_pulse_engine_bridge"]


def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    if action == "boot":
        from lab_os_boot import boot
        m = boot(
            force=bool(req.get("force")),
            workers=int(req.get("workers") or 2),
            isolate_dirty=req.get("isolate_dirty", True),
            seal_label=req.get("seal"),
            still_seconds=float(req.get("still") or 0),
            lo=req.get("lo"),
            hi=req.get("hi"),
        )
        st["boots"] = int(st.get("boots") or 0) + 1
        st["last"] = {"ok": m.get("ok"), "ms": m.get("ms"), "fingerprint": m.get("fingerprint")}
        _save(st)
        return {"status": "booted", **m, **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "boot"}), indent=2, default=str))
