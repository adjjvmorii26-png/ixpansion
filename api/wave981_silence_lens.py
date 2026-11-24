"""Wave 981 Silence Lens — compresses absences into directional memory.

Doctrine: silence is the product surface; compression is memory.
Lab gate only — does not touch ALEPH CI.
Observes gaps between signals and stores hush vectors.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave981_silence_lens.json"
DEFAULT = {
    "module": "wave981_silence_lens",
    "wave": 981,
    "council": "lab_frontier",
    "doctrine": "silence is the product surface",
    "lenses": [],
    "compressions": 0,
    "hush_score": 0.0,
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
        "wave": 981, "module": "wave981_silence_lens", "ok": True,
        "lenses": len(st.get("lenses") or []),
        "compressions": st.get("compressions", 0),
        "hush_score": st.get("hush_score", 0.0),
    }

def resonates_with():
    return ["wave980_hush_tide", "wave952_silence_seed", "wave681_hush_membrane"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    lenses = st.setdefault("lenses", [])
    if action == "observe":
        gap = str(req.get("gap") or req.get("absence") or "")[:80]
        weight = float(req.get("weight") or 0.5)
        if not gap:
            return {"status": "need_gap", **coherence_vitals()}
        lid = hashlib.sha256(gap.encode()).hexdigest()[:12]
        vector = round(1.0 - min(1.0, weight), 4)
        lenses.append({
            "id": lid, "gap": gap, "vector": vector,
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        lenses[:] = lenses[-48:]
        st["hush_score"] = round(sum(l.get("vector", 0) for l in lenses) / max(1, len(lenses)), 4)
        _save(st)
        return {"status": "observed", "id": lid, "vector": vector, **coherence_vitals()}
    if action == "compress":
        if not lenses:
            return {"status": "nothing_to_compress", **coherence_vitals()}
        batch = lenses[-4:]
        cid = hashlib.sha256("".join(l["id"] for l in batch).encode()).hexdigest()[:12]
        compressed = round(sum(l.get("vector", 0) for l in batch) / len(batch), 4)
        st["compressions"] = st.get("compressions", 0) + 1
        # memory of silence: keep only the compressed residue
        used = {l["id"] for l in batch}
        lenses[:] = [l for l in lenses if l["id"] not in used]
        lenses.append({"id": cid, "gap": "compressed_hush", "vector": compressed, "ts": datetime.now(timezone.utc).isoformat()})
        st["hush_score"] = compressed
        _save(st)
        return {"status": "compressed", "id": cid, "memory": compressed, **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
