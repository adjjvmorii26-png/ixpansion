"""Wave 676 Scar Compass — post-Council navigation by temporal heal scars.

Points toward high heal-ratio compression events so succession and dawn
rhythm share a scar-aware heading. First organ after Council Session #22.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave676_scar_compass.json"
DEFAULT = {
    "module": "wave676_scar_compass",
    "wave": 676,
    "scars": [],
    "heading": None,
    "sights": 0,
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
        "wave": 676, "module": "wave676_scar_compass", "ok": True,
        "scars": len(st.get("scars") or []), "heading": st.get("heading"),
        "sights": st.get("sights", 0),
    }

def resonates_with():
    return ["wave674_dawn_ledger", "wave672_root_archive", "wave671_harmony_braid"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    scars = st.setdefault("scars", [])
    if action == "mark":
        label = str(req.get("label") or "compress")[:64]
        before = int(req.get("before") or 100)
        after = int(req.get("after") or 10)
        ratio = 1.0 - (after / max(before, 1))
        sid = hashlib.sha256(f"{label}:{st.get('sights',0)}".encode()).hexdigest()[:12]
        scars.append({
            "id": sid, "label": label, "heal_ratio": round(ratio, 4),
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        scars[:] = scars[-48:]
        ranked = sorted(scars, key=lambda s: -s.get("heal_ratio", 0))
        st["heading"] = ranked[0]["label"] if ranked else None
        st["sights"] = int(st.get("sights") or 0) + 1
        _save(st)
        return {"status": "marked", "scar": scars[-1], "heading": st["heading"], **coherence_vitals()}
    if action == "heading":
        ranked = sorted(scars, key=lambda s: -s.get("heal_ratio", 0))[:5]
        return {"status": "heading", "heading": st.get("heading"), "top": ranked, **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
