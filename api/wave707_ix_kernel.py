"""Wave 707 IX Kernel — agent surface for the self-extending runtime."""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lab" / "ops"))
sys.path.insert(0, str(ROOT / "api"))

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave707_ix_kernel.json"
DEFAULT = {"module": "wave707_ix_kernel", "wave": 707, "ignitions": 0}


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
        "wave": 707, "module": "wave707_ix_kernel", "ok": True,
        "ignitions": st.get("ignitions", 0),
        "last_ok": last.get("ok"),
        "last_next_wave": last.get("next_wave"),
    }


def resonates_with():
    return ["wave706_lab_os_boot", "wave705_lab_jumpstart", "wave704_lab_epoch_seal"]


def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    if action == "ignite":
        from ix_kernel import ignite
        m = ignite(
            workers=int(req.get("workers") or 2),
            force=bool(req.get("force")),
            scaffold=bool(req.get("scaffold")),
            seal_label=req.get("seal"),
            captions=req.get("captions", True),
        )
        st["ignitions"] = int(st.get("ignitions") or 0) + 1
        st["last"] = {
            "ok": m.get("ok"),
            "ms": m.get("ms"),
            "fingerprint": m.get("fingerprint"),
            "next_wave": m.get("next_wave"),
        }
        _save(st)
        return {"status": "ignited", **m, **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
