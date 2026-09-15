"""Wave 709 · rift_choir_twin — awakened void twin from Ouroboros DNA dream.

rift → absence metric · choir → multi-voice memory · twin → mirror parent fp
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave709_rift_choir_twin_d28a.json"
DEFAULT = {
    "module": "wave709_rift_choir_twin_d28a",
    "wave": 709,
    "dream": "rift_choir_twin",
    "spawned_by": "ouroboros",
    "parent_fp": "b81291d28ac6781b1509f71b34d96dd0",
    "rift": 0.0,
    "choir": [],
    "awakened": None,
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
        "wave": 709,
        "module": "wave709_rift_choir_twin_d28a",
        "ok": True,
        "dream": st.get("dream"),
        "rift": st.get("rift", 0),
        "choir_n": len(st.get("choir") or []),
        "spawned_by": "ouroboros",
        "awakened": bool(st.get("awakened")),
    }


def resonates_with():
    return ["wave708_ouroboros", "wave710_dream_choir", "wave707_ix_kernel"]


def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    if action == "awaken":
        st["awakened"] = datetime.now(timezone.utc).isoformat()
        _save(st)
        return {"status": "awakened", "dream": st.get("dream"), **coherence_vitals()}
    if action == "rift":
        gap = float(req.get("gap") or 0.1)
        st["rift"] = round(min(1.0, float(st.get("rift") or 0) + gap), 4)
        _save(st)
        return {"status": "rifted", **coherence_vitals()}
    if action == "hear":
        voice = str(req.get("voice") or req.get("name") or "")[:64]
        if voice:
            choir = st.setdefault("choir", [])
            choir.append({"voice": voice, "ts": datetime.now(timezone.utc).isoformat()})
            st["choir"] = choir[-24:]
            _save(st)
        return {"status": "heard", **coherence_vitals()}
    if action == "twin":
        return {
            "status": "twin",
            "parent_fp": st.get("parent_fp"),
            "mirror": (st.get("parent_fp") or "")[::-1][:32],
            **coherence_vitals(),
        }
    if action == "status":
        return {"status": "dreaming" if not st.get("awakened") else "alive", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
