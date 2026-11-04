"""Wave 976 Edge Hush — measures residual hush at the edge of the braid.

Frontier organ after silence_margin (975).
Silence is the product surface. Does not replay prior organs.
Compression is memory. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave976_edge_hush.json"
DEFAULT = {
    "module": "wave976_edge_hush",
    "wave": 976,
    "council": "session_22_edge",
    "persona": "HUSH",
    "score": 0.0,
    "edges": [],
    "hush_token": "",
}

def _load():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return dict(DEFAULT)

def _save(st):
    DATA.mkdir(parents=True, exist_ok=True)
    try:
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(st, indent=2) + "\n")
        tmp.replace(STATE_FILE)
    except OSError:
        try:
            STATE_FILE.write_text(json.dumps(st, indent=2) + "\n")
        except OSError:
            pass

def coherence_vitals():
    st = _load()
    return {
        "wave": 976,
        "module": "wave976_edge_hush",
        "ok": True,
        "persona": "HUSH",
        "edges": len(st.get("edges") or []),
        "has_token": bool(st.get("hush_token")),
    }

def resonates_with():
    return [
        "wave671_harmony_braid",
        "wave675_consensus_bloom",
        "wave949_council_witness",
    ]

def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()
    edges = st.setdefault("edges", [])
    if action == "edge":
        source = str(req.get("source") or "braid")[:32]
        residual = float(req.get("residual") or 0.0)
        eid = hashlib.sha256(f"{source}:{residual}".encode()).hexdigest()[:10]
        edges.append({
            "id": eid,
            "source": source,
            "residual": round(residual, 4),
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        edges[:] = edges[-16:]
        _save(st)
        return {"status": "edged", "id": eid, **coherence_vitals()}
    if action == "hush":
        if not edges:
            return {"status": "no_edges", **coherence_vitals()}
        blob = "".join(e["id"] for e in edges[-4:])
        token = hashlib.sha256(blob.encode()).hexdigest()[:12]
        st["hush_token"] = token
        st["score"] = round(1.0 - min(1.0, sum(e.get("residual", 0) for e in edges[-4:]) / 4), 4)
        _save(st)
        return {"status": "hushed", "token": token, "score": st["score"], **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
