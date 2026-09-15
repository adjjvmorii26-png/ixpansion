"""Wave 676 Citizen Census — aggregate Citizen Rights into living demographics.

Roles, rights density, and participation rates as organism vital signs.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave676_citizen_census.json"
DEFAULT = {"module": "wave676_citizen_census", "wave": 676, "citizens": {}, "censuses": 0}

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
    return {"wave": 676, "module": "wave676_citizen_census", "ok": True,
            "citizens": len(st.get("citizens") or {}), "censuses": st.get("censuses", 0)}

def resonates_with():
    return ["wave666_citizen_rights", "wave658_sovereignty_beacon", "wave647_trust_network"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    citizens = st.setdefault("citizens", {})
    if action == "register":
        name = str(req.get("name") or f"c_{len(citizens)}")[:48]
        role = str(req.get("role") or "resident")[:32]
        rights = req.get("rights") or ["speak", "query"]
        citizens[name] = {"role": role, "rights": list(rights)[:12],
                          "since": datetime.now(timezone.utc).isoformat()}
        _save(st)
        return {"status": "registered", "name": name, **coherence_vitals()}
    if action == "census":
        roles = {}
        for c in citizens.values():
            r = c.get("role", "unknown")
            roles[r] = roles.get(r, 0) + 1
        rights_n = sum(len(c.get("rights") or []) for c in citizens.values())
        density = rights_n / max(len(citizens), 1)
        st["censuses"] = int(st.get("censuses") or 0) + 1
        report = {"roles": roles, "rights_density": round(density, 3), "population": len(citizens)}
        st["last_census"] = report
        _save(st)
        return {"status": "census", **report, **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
