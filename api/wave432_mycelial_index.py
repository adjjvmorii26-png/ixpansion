"""Wave 432 Mycelial Index — spores of memory under the homestead."""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone
DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave432_mycelial_index.json"
DEFAULT = {"module": "wave432_mycelial_index", "wave": 432, "spores": {}, "queries": 0}
def _load():
    if STATE_FILE.exists():
        try: return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError: pass
    return dict(DEFAULT)
def _save(state):
    DATA.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n")
def coherence_vitals():
    st = _load()
    return {"wave": 432, "module": "wave432_mycelial_index", "ok": True, "spores": len(st.get("spores") or {}), "queries": st.get("queries", 0)}
def resonates_with():
    return ["wave431_homestead", "wave428_resonance_chamber"]
def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    if action == "seed":
        key = str(req.get("key") or "doctrine"); note = str(req.get("note") or "")[:200]
        spores = st.setdefault("spores", {}); spores.setdefault(key, [])
        spores[key].append({"note": note, "ts": datetime.now(timezone.utc).isoformat()})
        spores[key] = spores[key][-20:]; _save(st)
        return {"status": "seeded", "key": key, "n": len(spores[key]), **coherence_vitals()}
    if action == "query":
        key = str(req.get("key") or ""); st["queries"] = int(st.get("queries") or 0) + 1; _save(st)
        return {"status": "query", "key": key, "hits": (st.get("spores") or {}).get(key, []), **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}
