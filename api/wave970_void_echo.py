"""Wave 970 Void Echo — compresses unanswered questions into silent residues.

Silence is the product surface. Compression is memory.
Does not answer. Only stores the weight of the unsaid.
Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave970_void_echo.json"
DEFAULT = {
    "module": "wave970_void_echo",
    "wave": 970,
    "residues": [],
    "weight": 0.0,
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
        "wave": 970, "module": "wave970_void_echo", "ok": True,
        "residues": len(st.get("residues") or []),
        "weight": st.get("weight", 0.0),
    }

def resonates_with():
    return ["wave675_consensus_bloom", "wave672_root_archive", "wave949_council_witness"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    residues = st.setdefault("residues", [])
    if action == "void":
        q = str(req.get("question") or req.get("q") or "")[:160]
        if not q:
            return {"status": "empty", **coherence_vitals()}
        rid = hashlib.sha256(q.encode()).hexdigest()[:12]
        weight = min(1.0, len(q) / 80.0)
        residues.append({
            "id": rid, "question": q, "weight": round(weight, 4),
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        residues[:] = residues[-48:]
        st["weight"] = round(sum(r.get("weight", 0) for r in residues[-8:]), 4)
        _save(st)
        return {"status": "voided", "id": rid, "residue_weight": weight, **coherence_vitals()}
    if action == "status":
        return {"status": "silent", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
