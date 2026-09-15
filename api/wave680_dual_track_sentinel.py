"""Wave 680 Dual-Track Sentinel — watches lab vs ALEPH contamination.

Innovative: scores path overlap risk between lab-scoped changes and ALEPH
monorepo surfaces; emits soft quarantine advisories without failing CI.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave680_dual_track_sentinel.json"
DEFAULT = {
    "module": "wave680_dual_track_sentinel",
    "wave": 680,
    "scans": 0,
    "risk": 0.0,
    "advisories": [],
}

LAB_PREFIXES = ("lab/", "api/wave", "tests/test_wave", "tests/test_council", ".github/workflows/lab-")
ALEPH_HOT = ("aleph_bot.py", "api/agents.py", "api/ai_gateway.py", "main.py", "cli.py")

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
        "wave": 680, "module": "wave680_dual_track_sentinel", "ok": True,
        "scans": st.get("scans", 0), "risk": st.get("risk", 0),
        "advisories": len(st.get("advisories") or []),
    }

def resonates_with():
    return ["wave676_scar_compass", "wave675_consensus_bloom", "wave671_harmony_braid"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    advisories = st.setdefault("advisories", [])
    if action == "scan":
        paths = req.get("paths") or []
        if isinstance(paths, str):
            paths = [p.strip() for p in paths.split(",") if p.strip()]
        lab_hits = sum(1 for p in paths if any(p.startswith(pre) or pre in p for pre in LAB_PREFIXES))
        aleph_hits = sum(1 for p in paths if any(h in p for h in ALEPH_HOT))
        n = max(len(paths), 1)
        mix = min(lab_hits, aleph_hits) / n
        risk = round(min(1.0, mix * 2.0 + (0.1 if aleph_hits and lab_hits else 0)), 4)
        st["risk"] = risk
        st["scans"] = int(st.get("scans") or 0) + 1
        if risk >= 0.3:
            advisories.append({
                "risk": risk, "lab_hits": lab_hits, "aleph_hits": aleph_hits,
                "advice": "split PR: lab path-filtered vs ALEPH core",
                "ts": datetime.now(timezone.utc).isoformat(),
            })
            advisories[:] = advisories[-16:]
        _save(st)
        return {
            "status": "scanned", "risk": risk, "lab_hits": lab_hits,
            "aleph_hits": aleph_hits, **coherence_vitals(),
        }
    if action == "advisories":
        return {"status": "advisories", "items": advisories[-5:], **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
