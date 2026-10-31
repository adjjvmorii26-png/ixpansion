"""Wave 973 Gap Lattice — lattice of silent intervals between organs.

Silence is the product surface. Compression is memory.
Records the uncommitted gaps; the product is the lattice of absences.
Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave973_gap_lattice.json"
DEFAULT = {
    "module": "wave973_gap_lattice",
    "wave": 973,
    "gaps": [],
    "lattice": [],
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
        "wave": 973, "module": "wave973_gap_lattice", "ok": True,
        "gaps": len(st.get("gaps") or []),
        "lattice": len(st.get("lattice") or []),
    }

def resonates_with():
    return ["wave972_hush_vector", "wave971_threshold_silence", "wave672_root_archive"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    gaps = st.setdefault("gaps", [])
    lattice = st.setdefault("lattice", [])
    if action == "record":
        left = str(req.get("left") or req.get("a") or "")[:48]
        right = str(req.get("right") or req.get("b") or "")[:48]
        width = min(1.0, max(0.0, float(req.get("width") or req.get("silence") or 0.4)))
        if not left or not right:
            return {"status": "need_pair", **coherence_vitals()}
        gid = hashlib.sha256(f"{left}:{right}:{width}".encode()).hexdigest()[:12]
        gap = {
            "id": gid, "left": left, "right": right, "width": width,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        gaps.append(gap)
        gaps[:] = gaps[-64:]
        _save(st)
        return {"status": "recorded", "id": gid, **coherence_vitals()}
    if action == "weave":
        if len(gaps) < 2:
            return {"status": "need_gaps", **coherence_vitals()}
        batch = gaps[-3:]
        lid = hashlib.sha256("".join(g["id"] for g in batch).encode()).hexdigest()[:12]
        density = round(sum(g.get("width", 0) for g in batch) / len(batch), 4)
        entry = {
            "id": lid, "members": [g["id"] for g in batch],
            "density": density,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        lattice.append(entry)
        lattice[:] = lattice[-32:]
        _save(st)
        return {"status": "woven", "lattice": entry, **coherence_vitals()}
    if action == "status":
        return {"status": "latticed", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
