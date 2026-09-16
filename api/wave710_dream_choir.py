"""Wave 710 Dream Choir — many DNA dreams → one resonance map."""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lab" / "ops"))
sys.path.insert(0, str(ROOT / "api"))

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave710_dream_choir.json"
DEFAULT = {"module": "wave710_dream_choir", "wave": 710, "choirs": 0}


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
        "wave": 710, "module": "wave710_dream_choir", "ok": True,
        "choirs": st.get("choirs", 0),
        "last_dominant": last.get("dominant"),
    }


def resonates_with():
    return ["wave708_ouroboros", "wave709_rift_choir_twin_d28a", "wave707_ix_kernel"]



def _self_sing(voices: int = 5) -> dict:
    """Self-contained choir: harmonic resonance without lab dependencies."""
    import math, random
    try:
        voices = max(1, min(int(voices), 16))
    except (TypeError, ValueError):
        voices = 5
    notes = []
    for i in range(voices):
        freq = 220.0 * (2 ** (i / 12.0))
        amp = 0.4 + 0.5 * random.random()
        notes.append({"voice": i, "freq": round(freq, 2), "amp": round(amp, 3)})
    dominant = max(notes, key=lambda n: n["amp"])
    return {
        "ok": True, "voices": voices, "notes": notes, "dominant": dominant,
        "resonance": round(sum(n["amp"] for n in notes) / voices, 3),
    }

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    if action in ("sing", "choir"):
        voices = int(req.get("voices") or 5)
        try:
            from dream_choir import sing
            m = sing(voices=voices, force=bool(req.get("force")))
        except Exception:
            m = _self_sing(voices)
        st["choirs"] = int(st.get("choirs") or 0) + 1
        resonance = m.get("resonance")
        dominant = resonance.get("dominant") if isinstance(resonance, dict) else resonance
        st["last"] = {
            "dominant": dominant,
            "voices": m.get("voices"),
            "ms": m.get("ms"),
        }
        _save(st)
        return {"status": "sung", **m, **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "sing", "voices": 3}), indent=2, default=str))
