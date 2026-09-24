"""Wave 937 — experiment_track_hygiene.

Refine dual-track awareness:
- List 900-series organs present on main (api/wave9*.py)
- Cross-check against experiment_queue_atlas open-PR seed
- Flag "landed but PR still open" and "queued but missing on main"

Does not merge PRs. Silence is the product surface.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave937_experiment_track_hygiene.json"
API = ROOT / "api"
WAVE = 937
NAME = "experiment_track_hygiene"

DEFAULT = {"wave": WAVE, "name": NAME, "scans": 0, "status": "idle"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load() -> dict:
    if STATE_FILE.exists():
        try:
            raw = json.loads(STATE_FILE.read_text())
            if isinstance(raw, dict):
                return raw
        except Exception:
            pass
    return dict(DEFAULT)


def _save(st: dict) -> None:
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


def _import_api(mod: str):
    if str(API) not in sys.path:
        sys.path.insert(0, str(API))
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    return __import__(mod)


def _on_main_experiment_waves() -> list:
    found = []
    if not API.is_dir():
        return found
    for p in API.glob("wave*.py"):
        m = re.match(r"wave(\d+)_", p.name)
        if m:
            n = int(m.group(1))
            if n >= 900:
                found.append(n)
    return sorted(set(found))


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave937_experiment_track_hygiene",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "scans": int(st.get("scans") or 0),
        "resonance": round(min(1.0, 0.5 + int(st.get("scans") or 0) * 0.02), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave812_experiment_queue_atlas",
        "wave816_ci_gate_mirror",
        "wave822_gate_priority",
        "wave823_pytest_collection_gate",
        "wave787_dual_track_pr_bot",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "scan":
        on_main = _on_main_experiment_waves()
        queued = []
        try:
            atlas = _import_api("wave812_experiment_queue_atlas")
            q = atlas.handler({"action": "status"}).get("queue") or []
            queued = [int(x.get("wave") or 0) for x in q if x.get("wave")]
        except Exception:
            queued = []
        landed_still_queued = sorted(set(on_main) & set(queued))
        queued_missing = sorted(set(queued) - set(on_main))
        report = {
            "on_main_900plus": on_main[-24:],
            "queued": queued,
            "landed_still_queued": landed_still_queued,
            "queued_missing_on_main": queued_missing,
            "advice": (
                "close or merge open experiment PRs whose waves already exist on main; "
                "dual-track: lab CI ≠ experiment PR auto-merge"
            ),
            "ts": _now(),
        }
        st["scans"] = int(st.get("scans") or 0) + 1
        st["status"] = "scanned"
        st["last_report"] = report
        _save(st)
        return {
            **coherence_vitals(),
            "status": "scanned",
            "report": report,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("scans") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"experiment track hygiene scans {n}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "scan"}), indent=2))
