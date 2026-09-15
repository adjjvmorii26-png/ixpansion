"""Wave 672 Epoch Compass — navigates proposed futures from Epoch Forge.

Points toward high-resonance / low-entropy wave proposals; records bearings
so succession and sovereignty organs share a common heading.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave672_epoch_compass.json"
DEFAULT = {"module": "wave672_epoch_compass", "wave": 672, "bearings": [], "heading": None}

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
    return {"wave": 672, "module": "wave672_epoch_compass", "ok": True,
            "bearings": len(st.get("bearings") or []), "heading": st.get("heading")}

def resonates_with():
    return ["wave659_epoch_forge", "wave657_succession_planner", "wave658_sovereignty_beacon"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    bearings = st.setdefault("bearings", [])
    if action == "sight":
        label = str(req.get("label") or f"future_{len(bearings)}")[:64]
        resonance = float(req.get("resonance") or 0.5)
        entropy = float(req.get("entropy") or 0.5)
        score = resonance - 0.4 * entropy
        b = {"label": label, "resonance": resonance, "entropy": entropy,
             "score": round(score, 4), "ts": datetime.now(timezone.utc).isoformat()}
        bearings.append(b)
        bearings[:] = bearings[-48:]
        ranked = sorted(bearings, key=lambda x: -x["score"])
        st["heading"] = ranked[0]["label"] if ranked else None
        _save(st)
        return {"status": "sighted", "bearing": b, "heading": st["heading"], **coherence_vitals()}
    if action == "heading":
        return {"status": "heading", "heading": st.get("heading"), "top": sorted(bearings, key=lambda x: -x["score"])[:5],
                **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
