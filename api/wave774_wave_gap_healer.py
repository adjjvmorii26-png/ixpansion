"""Wave 774 — wave_gap_healer.

Surveys wave ID gaps without forcing sequential fills.
Ghost markers only — optional soft register. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = ROOT / "api"
DATA = ROOT / "data"
STATE_FILE = DATA / "wave774_wave_gap_healer.json"
WAVE = 774
NAME = "wave_gap_healer"
WAVE_RE = re.compile(r"^wave(\d+)_([a-z0-9_]+)\.py$")

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "surveys": 0,
    "last_gap_count": 0,
    "ghosts": [],
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


def _inventory():
    waves = []
    if API.is_dir():
        for p in API.glob("wave*.py"):
            m = WAVE_RE.match(p.name)
            if m:
                waves.append((int(m.group(1)), m.group(2)))
    waves.sort(key=lambda x: x[0])
    nums = [n for n, _ in waves]
    return nums, waves


def _gaps(nums, window=100):
    if not nums:
        return []
    hi = max(nums)
    lo = max(min(nums), hi - window)
    present = set(nums)
    return [i for i in range(lo, hi + 1) if i not in present]


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave774_wave_gap_healer",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "surveys": int(st.get("surveys") or 0),
        "last_gap_count": int(st.get("last_gap_count") or 0),
        "ghosts": len(st.get("ghosts") or []),
        "resonance": round(min(1.0, 0.5 + int(st.get("surveys") or 0) * 0.01), 4),
        "surface": "silence",
        "policy": "survey_not_force_fill",
    }


def resonates_with() -> list:
    return [
        "wave773_ci_sentinel_bridge",
        "lab.ops.copilots.helix",
        "wave770_copilot_council_pulse",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "survey":
        window = int(req.get("window") or 100)
        nums, waves = _inventory()
        gaps = _gaps(nums, window=window)
        st["surveys"] = int(st.get("surveys") or 0) + 1
        st["last_gap_count"] = len(gaps)
        st["status"] = "surveyed"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "surveyed",
            "wave_count": len(nums),
            "latest": nums[-1] if nums else 0,
            "gaps": gaps[:40],
            "gap_count": len(gaps),
            "recent": [{"n": n, "slug": s} for n, s in waves[-6:]],
            "advice": "Do not force-fill gaps; optional ghost only",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "ghost":
        n = int(req.get("n") or 0)
        reason = str(req.get("reason") or "intentional_absence")[:80]
        if n <= 0:
            return {**coherence_vitals(), "status": "bad_n", "audio": False}
        ghosts = [g for g in list(st.get("ghosts") or []) if g.get("n") != n]
        ghosts.append({"n": n, "reason": reason, "ts": _now()})
        st["ghosts"] = ghosts[-64:]
        st["status"] = "ghosted"
        _save(st)
        return {
            **coherence_vitals(),
            "status": "ghosted",
            "ghost": {"n": n, "reason": reason},
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        g = int(st.get("last_gap_count") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"gaps {g} · ghosts {len(st.get('ghosts') or [])}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "survey"}), indent=2))
