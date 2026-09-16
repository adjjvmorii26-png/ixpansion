"""Wave 738 Oblivion Compost — intentional death + nutrient reuse."""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave738_oblivion_compost.json"
DEFAULT = {"module": "wave738_oblivion_compost", "wave": 738, "tombstones": [], "nutrients": 0.0}


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
    return {"wave": 738, "module": "wave738_oblivion_compost", "ok": True,
            "tombstones": len(st.get("tombstones") or []), "nutrients": st.get("nutrients", 0)}


def resonates_with():
    return ["wave735_antimeme_vaccine", "wave672_root_archive", "wave708_ouroboros"]


def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    tombs = st.setdefault("tombstones", [])
    if action == "compost":
        name = str(req.get("module") or req.get("name") or "")[:80]
        if not name: return {"status": "empty", **coherence_vitals()}
        nutrient = float(req.get("nutrient") or 1.0)
        tid = hashlib.sha256(f"{name}:{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:12]
        stone = {"id": tid, "module": name, "nutrient": nutrient,
                 "ts": datetime.now(timezone.utc).isoformat(), "ghost": True}
        tombs.append(stone)
        st["tombstones"] = tombs[-96:]
        st["nutrients"] = round(float(st.get("nutrients") or 0) + nutrient, 4)
        _save(st)
        return {"status": "composted", "tombstone": stone, **coherence_vitals()}
    if action == "draw":
        need, have = float(req.get("amount") or 1.0), float(st.get("nutrients") or 0)
        if need > have: return {"status": "insufficient", "have": have, **coherence_vitals()}
        st["nutrients"] = round(have - need, 4)
        _save(st)
        return {"status": "drawn", "amount": need, "remaining": st["nutrients"], **coherence_vitals()}
    if action == "rehydrate":
        tid = str(req.get("id") or "")
        for t in tombs:
            if t.get("id") == tid:
                return {"status": "ghost", "tombstone": t, **coherence_vitals()}
        return {"status": "not_found", **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
