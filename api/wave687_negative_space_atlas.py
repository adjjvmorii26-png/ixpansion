"""Wave 687 Negative Space Atlas — maps what the organism deliberately omits.

Experimental: builds a graph of intentional absences (skipped modules, deferred
features, pruned routes) so agents can query the shape of the void instead of
only the shape of presence. Negative space becomes navigable structure.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave687_negative_space_atlas.json"
DEFAULT = {
    "module": "wave687_negative_space_atlas",
    "wave": 687,
    "voids": {},
    "edges": [],
    "queries": 0,
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
        "wave": 687, "module": "wave687_negative_space_atlas", "ok": True,
        "voids": len(st.get("voids") or {}),
        "edges": len(st.get("edges") or []),
        "queries": st.get("queries", 0),
    }

def resonates_with():
    return ["wave683_void_meter", "wave672_root_archive", "wave681_hush_membrane"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    voids = st.setdefault("voids", {})
    edges = st.setdefault("edges", [])
    if action == "omit":
        name = str(req.get("name") or req.get("path") or "")[:80]
        reason = str(req.get("reason") or "deferred")[:64]
        if not name:
            return {"status": "empty", **coherence_vitals()}
        vid = hashlib.sha256(name.encode()).hexdigest()[:12]
        voids[vid] = {
            "name": name, "reason": reason,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        parent = str(req.get("near") or "")
        if parent and parent in voids:
            edges.append({"from": parent, "to": vid, "kind": "adjacent_absence"})
            edges[:] = edges[-64:]
        _save(st)
        return {"status": "omitted", "id": vid, **coherence_vitals()}
    if action == "query":
        st["queries"] = int(st.get("queries") or 0) + 1
        q = str(req.get("q") or "").lower()
        hits = [v for v in voids.values() if q in v.get("name", "").lower() or q in v.get("reason", "").lower()]
        _save(st)
        return {"status": "queried", "hits": hits[:12], **coherence_vitals()}
    if action == "atlas":
        return {"status": "atlas", "voids": voids, "edges": edges[-20:], **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
