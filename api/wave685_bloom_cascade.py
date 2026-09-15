"""Wave 679 Bloom Cascade — chains consensus blooms into capability trees.

Innovative: each bloomed capability can parent child proposals; cascade depth
unlocks compound organs without manual wiring.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave685_bloom_cascade.json"
DEFAULT = {
    "module": "wave685_bloom_cascade",
    "wave": 685,
    "nodes": {},
    "edges": [],
    "depth_max": 0,
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
        "wave": 685, "module": "wave685_bloom_cascade", "ok": True,
        "nodes": len(st.get("nodes") or {}),
        "edges": len(st.get("edges") or []),
        "depth_max": st.get("depth_max", 0),
    }

def resonates_with():
    return ["wave675_consensus_bloom", "wave673_naming_well", "wave671_harmony_braid"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    nodes = st.setdefault("nodes", {})
    edges = st.setdefault("edges", [])
    if action == "root":
        name = str(req.get("name") or req.get("capability") or "")[:64]
        if not name:
            return {"status": "empty", **coherence_vitals()}
        nid = hashlib.sha256(name.encode()).hexdigest()[:12]
        nodes[nid] = {"name": name, "depth": 0, "ts": datetime.now(timezone.utc).isoformat()}
        _save(st)
        return {"status": "rooted", "id": nid, **coherence_vitals()}
    if action == "branch":
        parent = str(req.get("parent") or "")
        name = str(req.get("name") or "")[:64]
        if parent not in nodes or not name:
            return {"status": "invalid", **coherence_vitals()}
        cid = hashlib.sha256(f"{parent}:{name}".encode()).hexdigest()[:12]
        depth = int(nodes[parent].get("depth", 0)) + 1
        nodes[cid] = {"name": name, "depth": depth, "parent": parent,
                      "ts": datetime.now(timezone.utc).isoformat()}
        edges.append({"parent": parent, "child": cid})
        edges[:] = edges[-64:]
        st["depth_max"] = max(int(st.get("depth_max") or 0), depth)
        _save(st)
        return {"status": "branched", "id": cid, "depth": depth, **coherence_vitals()}
    if action == "tree":
        return {"status": "tree", "nodes": nodes, "edges": edges[-20:], **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
