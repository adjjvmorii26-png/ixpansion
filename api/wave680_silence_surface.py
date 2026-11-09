"""Wave 680 Silence Surface — silence is the product surface.

Doctrine: silence is the product surface; compression is memory;
lab gates ≠ ALEPH full CI.
Observes hush intervals and compresses residual noise into durable residues.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave680_silence_surface.json"
DEFAULT = {
    "module": "wave680_silence_surface",
    "wave": 680,
    "council": "lab_frontier",
    "persona": "HUSH",
    "score": 0.0,
    "intervals": [],
    "residues": [],
    "charge": 0.0,
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
        "wave": 680, "module": "wave680_silence_surface", "ok": True,
        "persona": "HUSH", "intervals": len(st.get("intervals") or []),
        "residues": len(st.get("residues") or []), "charge": st.get("charge", 0),
    }

def resonates_with():
    return ["wave672_root_archive", "wave674_dawn_ledger", "wave675_consensus_bloom"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    intervals = st.setdefault("intervals", [])
    residues = st.setdefault("residues", [])
    if action == "observe":
        duration = float(req.get("duration") or 1.0)
        residual = str(req.get("residual") or "")[:80]
        iid = hashlib.sha256(f"{duration}:{residual}:{len(intervals)}".encode()).hexdigest()[:10]
        intervals.append({
            "id": iid, "duration": duration, "residual": residual,
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        intervals[:] = intervals[-48:]
        st["charge"] = round(float(st.get("charge") or 0) + duration * 0.1, 4)
        _save(st)
        return {"status": "observed", "id": iid, "charge": st["charge"], **coherence_vitals()}
    if action == "compress":
        if not intervals:
            return {"status": "no_intervals", **coherence_vitals()}
        batch = intervals[-3:]
        residual_blob = "|".join(i.get("residual", "") for i in batch)
        rid = hashlib.sha256(residual_blob.encode()).hexdigest()[:12]
        compressed = hashlib.sha256(residual_blob.encode()).hexdigest()[:16]
        residues.append({
            "id": rid, "compressed": compressed,
            "from": [i["id"] for i in batch],
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        residues[:] = residues[-32:]
        used = {i["id"] for i in batch}
        intervals[:] = [i for i in intervals if i["id"] not in used]
        st["charge"] = max(0.0, round(float(st.get("charge") or 0) - len(batch) * 0.05, 4))
        st["score"] = round(min(1.0, float(st.get("score") or 0) + 0.05), 4)
        _save(st)
        return {"status": "compressed", "residue": residues[-1], "score": st["score"], **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
