"""Wave 966 — ci_sentinel.

Triage CI failures into flaky vs structural.
Quarantine lab-induced noise so ALEPH stays clean.
Does not run real CI. No payload. Silence is the product surface.
Lab organ only. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave966_ci_sentinel.json"
WAVE = 966
NAME = "ci_sentinel"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "triages": 0,
    "last_class": "idle",
    "quarantined": 0,
    "status": "idle",
}


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


def _classify(job: str, branch: str, message: str) -> str:
    """Heuristic: lab branches + smoke timeouts → flaky/lab; else structural."""
    j = (job or "").lower()
    b = (branch or "").lower()
    m = (message or "").lower()
    if b.startswith("lab/") or "lab" in b:
        return "lab_noise"
    if "timeout" in m or "flaky" in m or "smoke" in j:
        return "flaky"
    if "syntax" in m or "import" in m or "assert" in m:
        return "structural"
    return "unknown"


def coherence_vitals() -> dict:
    st = _load()
    triages = int(st.get("triages") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave966_ci_sentinel",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "triages": triages,
        "last_class": st.get("last_class", "idle"),
        "quarantined": int(st.get("quarantined") or 0),
        "resonance": round(min(1.0, 0.5 + triages * 0.015), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave686_dual_track_sentinel",
        "wave950_hush_margin",
        "wave949_council_witness",
        "wave773_ci_sentinel",  # historical lab note
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "triage":
        job = str(req.get("job") or "")
        branch = str(req.get("branch") or "")
        message = str(req.get("message") or "")
        klass = _classify(job, branch, message)
        st["triages"] = int(st.get("triages") or 0) + 1
        st["last_class"] = klass
        st["last_job"] = job
        st["last_branch"] = branch
        st["status"] = "triaged"
        st["last_ts"] = _now()
        if klass == "lab_noise":
            st["quarantined"] = int(st.get("quarantined") or 0) + 1
        _save(st)
        return {
            **coherence_vitals(),
            "status": "triaged",
            "class": klass,
            "quarantine": klass == "lab_noise",
            "caption": f"ci sentinel · {klass}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "quarantine":
        st["quarantined"] = int(st.get("quarantined") or 0) + 1
        st["status"] = "quarantined"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "quarantined",
            "caption": f"quarantine · {st['quarantined']}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"sentinel · {st.get('last_class', 'idle')} · q{st.get('quarantined', 0)}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "triage", "job": "vercel-runtime-smoke", "branch": "lab/wave953", "message": "timeout"}), indent=2))
