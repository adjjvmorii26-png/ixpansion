"""Wave 458 Soft Fork Garden — parallel experimental branches that never hard-fork main.

Experimental: plant soft forks (named experiment lanes). They accumulate proof
density independently; only a bloom/consensus action promotes a lane. No git
fork required — pure organism memory.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave458_soft_fork_garden.json"
DEFAULT = {
    "module": "wave458_soft_fork_garden",
    "wave": 458,
    "lanes": {},
    "promotions": [],
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
        "wave": 458, "module": "wave458_soft_fork_garden", "ok": True,
        "lanes": len(st.get("lanes") or {}),
        "promotions": len(st.get("promotions") or []),
    }

def resonates_with():
    return ["wave675_consensus_bloom", "wave453_semantic_scar_router", "wave679_bloom_cascade"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    lanes = st.setdefault("lanes", {})
    promotions = st.setdefault("promotions", [])
    if action == "plant":
        name = str(req.get("name") or "")[:48]
        if not name:
            return {"status": "empty", **coherence_vitals()}
        lid = hashlib.sha256(name.encode()).hexdigest()[:10]
        lanes[lid] = {
            "name": name, "proof": 0.0,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        _save(st)
        return {"status": "planted", "id": lid, **coherence_vitals()}
    if action == "nourish":
        lid = str(req.get("id") or "")
        amount = float(req.get("amount") or 0.1)
        if lid not in lanes:
            return {"status": "unknown_lane", **coherence_vitals()}
        lanes[lid]["proof"] = round(float(lanes[lid].get("proof") or 0) + amount, 4)
        _save(st)
        return {"status": "nourished", "id": lid, "proof": lanes[lid]["proof"], **coherence_vitals()}
    if action == "promote":
        lid = str(req.get("id") or "")
        threshold = float(req.get("threshold") or 1.0)
        if lid not in lanes:
            return {"status": "unknown_lane", **coherence_vitals()}
        if float(lanes[lid].get("proof") or 0) < threshold:
            return {"status": "underproof", "proof": lanes[lid]["proof"], **coherence_vitals()}
        promotions.append({
            "id": lid, "name": lanes[lid]["name"], "proof": lanes[lid]["proof"],
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        promotions[:] = promotions[-24:]
        _save(st)
        return {"status": "promoted", "lane": lanes[lid], **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
