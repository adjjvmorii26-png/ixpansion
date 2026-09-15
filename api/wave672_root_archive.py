"""Wave 672 Root Archive (CYTHARA) — retired waves get a ghost home + echo.

Council Session #22 sealed · score 0.734
Memory = identity. Retired organs live as ghosts; echoes can be queried.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave672_root_archive.json"
DEFAULT = {
    "module": "wave672_root_archive",
    "wave": 672,
    "council": "session_22",
    "persona": "CYTHARA",
    "score": 0.734,
    "ghosts": [],
    "echoes": [],
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
        "wave": 672, "module": "wave672_root_archive", "ok": True,
        "persona": "CYTHARA", "ghosts": len(st.get("ghosts") or []),
        "echoes": len(st.get("echoes") or []),
    }

def resonates_with():
    return ["wave660_lineage_crystal", "wave659_epoch_forge", "wave651_self_repair"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    ghosts = st.setdefault("ghosts", [])
    echoes = st.setdefault("echoes", [])
    if action == "retire":
        name = str(req.get("name") or req.get("wave") or "")[:64]
        if not name:
            return {"status": "no_name", **coherence_vitals()}
        gid = hashlib.sha256(name.encode()).hexdigest()[:12]
        ghosts.append({
            "id": gid, "name": name,
            "note": str(req.get("note") or "retired")[:120],
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        ghosts[:] = ghosts[-80:]
        _save(st)
        return {"status": "retired", "ghost": ghosts[-1], **coherence_vitals()}
    if action == "echo":
        name = str(req.get("name") or "")[:64]
        matches = [g for g in ghosts if name.lower() in g.get("name", "").lower()] if name else ghosts[-5:]
        for g in matches[:5]:
            echoes.append({
                "ghost_id": g["id"], "name": g["name"],
                "ts": datetime.now(timezone.utc).isoformat(),
            })
        echoes[:] = echoes[-48:]
        _save(st)
        return {"status": "echoed", "matches": matches[:5], **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
