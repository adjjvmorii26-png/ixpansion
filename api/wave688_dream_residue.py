"""Wave 688 Dream Residue — unfinished agent traces become recoverable dream material.

Experimental: when a task is interrupted or soft-failed, its partial state vector
is stored as residue. Later agents can inhale residue to resume, remix, or seed
new intents without replaying from zero. Dreams are first-class memory.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave688_dream_residue.json"
DEFAULT = {
    "module": "wave688_dream_residue",
    "wave": 688,
    "residues": [],
    "inhaled": 0,
    "capacity": 48,
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
        "wave": 688, "module": "wave688_dream_residue", "ok": True,
        "residues": len(st.get("residues") or []),
        "inhaled": st.get("inhaled", 0),
        "capacity": st.get("capacity", 48),
    }

def resonates_with():
    return ["wave672_root_archive", "wave681_hush_membrane", "wave687_negative_space_atlas"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    residues = st.setdefault("residues", [])
    cap = int(st.get("capacity") or 48)
    if action == "deposit":
        label = str(req.get("label") or "interrupted")[:64]
        fragment = str(req.get("fragment") or req.get("state") or "")[:512]
        source = str(req.get("source") or "agent")[:32]
        rid = hashlib.sha256(f"{label}:{fragment[:32]}".encode()).hexdigest()[:12]
        residues.append({
            "id": rid, "label": label, "fragment": fragment, "source": source,
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        residues[:] = residues[-cap:]
        _save(st)
        return {"status": "deposited", "id": rid, **coherence_vitals()}
    if action == "inhale":
        if not residues:
            return {"status": "empty", **coherence_vitals()}
        want = str(req.get("id") or "")
        pick = None
        if want:
            for r in residues:
                if r.get("id") == want:
                    pick = r
                    break
        if pick is None:
            pick = residues[-1]
            residues.pop()
        else:
            residues[:] = [r for r in residues if r.get("id") != want]
        st["inhaled"] = int(st.get("inhaled") or 0) + 1
        _save(st)
        return {"status": "inhaled", "residue": pick, **coherence_vitals()}
    if action == "list":
        return {"status": "list", "items": residues[-10:], **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
