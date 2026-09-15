"""Wave 708 Ouroboros — agent surface for infinite DNA-dream recurrence."""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lab" / "ops"))
sys.path.insert(0, str(ROOT / "api"))

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave708_ouroboros.json"
DEFAULT = {"module": "wave708_ouroboros", "wave": 708, "recurrences": 0}


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
        "wave": 708, "module": "wave708_ouroboros", "ok": True,
        "recurrences": st.get("recurrences", 0),
        "last_dream": last.get("dream"),
        "leap": "infinite",
    }


def resonates_with():
    return ["wave707_ix_kernel", "wave706_lab_os_boot", "wave703_proof_delta"]


def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    if action in ("recur", "once", "cycle"):
        from ouroboros import run
        m = run(
            cycles=int(req.get("cycles") or 1),
            scaffold=bool(req.get("scaffold", True)),
            force=bool(req.get("force")),
            dream_only=bool(req.get("dream_only")),
        )
        dream = (m.get("latest_dream") or {}).get("name")
        st["recurrences"] = int(st.get("recurrences") or 0) + int(m.get("cycles") or 1)
        st["last"] = {"dream": dream, "ok": m.get("ok"), "ms": m.get("ms")}
        _save(st)
        return {"status": "recurred", **m, **coherence_vitals()}
    if action == "dream":
        from ouroboros import run
        m = run(cycles=1, scaffold=False, dream_only=True)
        return {"status": "dreamed", **m, **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "dream"}), indent=2, default=str))
