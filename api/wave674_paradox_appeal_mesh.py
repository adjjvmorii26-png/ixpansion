"""Wave 674 Paradox Appeal Mesh — federates Paradox Court appeals across nodes.

Appeals can be mirrored; rulings propagate with weighted precedent strength.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave674_paradox_appeal_mesh.json"
DEFAULT = {"module": "wave674_paradox_appeal_mesh", "wave": 674, "appeals": [], "rulings": []}

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
    return {"wave": 674, "module": "wave674_paradox_appeal_mesh", "ok": True,
            "appeals": len(st.get("appeals") or []), "rulings": len(st.get("rulings") or [])}

def resonates_with():
    return ["wave669_paradox_appeal", "wave664_paradox_court", "wave665_mycelial_network"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    appeals = st.setdefault("appeals", [])
    rulings = st.setdefault("rulings", [])
    if action == "file":
        claim = str(req.get("claim") or "")[:160]
        if not claim:
            return {"status": "empty", **coherence_vitals()}
        aid = hashlib.sha256(claim.encode()).hexdigest()[:12]
        appeals.append({"id": aid, "claim": claim, "ts": datetime.now(timezone.utc).isoformat()})
        appeals[:] = appeals[-64:]
        _save(st)
        return {"status": "filed", "id": aid, **coherence_vitals()}
    if action == "rule":
        aid = str(req.get("id") or "")
        decision = str(req.get("decision") or "sustain").lower()
        strength = float(req.get("strength") or 0.7)
        target = next((a for a in appeals if a["id"] == aid), None)
        if not target:
            return {"status": "not_found", **coherence_vitals()}
        ruling = {"id": aid, "decision": decision, "strength": strength,
                  "ts": datetime.now(timezone.utc).isoformat()}
        rulings.append(ruling)
        rulings[:] = rulings[-64:]
        _save(st)
        return {"status": "ruled", "ruling": ruling, **coherence_vitals()}
    if action == "precedent":
        ranked = sorted(rulings, key=lambda r: -r.get("strength", 0))[:10]
        return {"status": "precedent", "top": ranked, **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
