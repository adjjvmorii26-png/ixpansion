"""Wave 680 Organism Horizon — the 680-wave vantage organ.

Collapses ontology crystal + epoch compass + heuristic canopy + sovereign seal
into a single horizon report: where the organism stands, what it is heading
toward, and what it has sealed as permanent.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave680_organism_horizon.json"
DEFAULT = {"module": "wave680_organism_horizon", "wave": 680, "reports": 0, "last": None}

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
    return {"wave": 680, "module": "wave680_organism_horizon", "ok": True,
            "reports": st.get("reports", 0), "has_last": bool(st.get("last"))}

def resonates_with():
    return [
        "wave671_ontology_crystal", "wave672_epoch_compass", "wave673_heuristic_garden",
        "wave678_sovereign_seal", "wave659_epoch_forge", "wave670_sentient_heuristic",
    ]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    if action == "survey":
        sys.path.insert(0, str(ROOT / "api"))
        pieces = {}
        try:
            import wave671_ontology_crystal as oc
            oc.handler({"action": "crystallize"})
            pieces["ontology"] = oc.handler({"action": "query", "q": "sovereignty silence proof"})
        except Exception as e:
            pieces["ontology"] = {"err": str(e)}
        try:
            import wave672_epoch_compass as ec
            ec.handler({"action": "sight", "label": "wave681+", "resonance": 0.85, "entropy": 0.2})
            pieces["compass"] = ec.handler({"action": "heading"})
        except Exception as e:
            pieces["compass"] = {"err": str(e)}
        try:
            import wave673_heuristic_garden as hg
            hg.handler({"action": "plant", "name": "horizon_policy", "weight": 0.7})
            hg.handler({"action": "water", "name": "horizon_policy", "success": True})
            pieces["canopy"] = hg.handler({"action": "canopy"})
        except Exception as e:
            pieces["canopy"] = {"err": str(e)}
        try:
            import wave678_sovereign_seal as ss
            pieces["seal"] = ss.handler({"action": "seal", "autonomy": 0.91, "deps": ["lab", "aleph"]})
        except Exception as e:
            pieces["seal"] = {"err": str(e)}

        report = {
            "wave": 680,
            "pieces": pieces,
            "caption": "organism horizon · wave 680 · silence holds · heading open",
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        st["last"] = report
        st["reports"] = int(st.get("reports") or 0) + 1
        _save(st)
        return {"status": "surveyed", **report, **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
