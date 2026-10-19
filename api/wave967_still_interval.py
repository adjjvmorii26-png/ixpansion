"""Wave 967 — still_interval.

Measure the silent gap between successive pulse or CI events.
The interval itself is the product. No replay. No payload.
Lab organ only. Lab gates ≠ ALEPH CI. Silence is the product surface.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave967_still_interval.json"
WAVE = 967
NAME = "still_interval"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "intervals": 0,
    "last_gap_s": 0.0,
    "longest_gap_s": 0.0,
    "status": "idle",
    "last_event_ts": None,
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_ts(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


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


def coherence_vitals() -> dict:
    st = _load()
    intervals = int(st.get("intervals") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave967_still_interval",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "intervals": intervals,
        "last_gap_s": float(st.get("last_gap_s") or 0),
        "longest_gap_s": float(st.get("longest_gap_s") or 0),
        "resonance": round(min(1.0, 0.52 + intervals * 0.012), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave966_ci_sentinel",
        "wave950_hush_margin",
        "wave944_hush_still",
        "wave790_still_interval",  # earlier still notes
        "wave681_hush_membrane",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "mark":
        # Record an event and compute gap from previous
        now = datetime.now(timezone.utc)
        prev = _parse_ts(st.get("last_event_ts"))
        gap = 0.0
        if prev is not None:
            gap = max(0.0, (now - prev).total_seconds())
        st["intervals"] = int(st.get("intervals") or 0) + 1
        st["last_gap_s"] = round(gap, 3)
        st["longest_gap_s"] = max(float(st.get("longest_gap_s") or 0), gap)
        st["last_event_ts"] = now.isoformat()
        st["status"] = "marked"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "marked",
            "gap_s": round(gap, 3),
            "caption": f"still interval · {round(gap, 1)}s",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        gap = float(st.get("last_gap_s") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"still · {round(gap, 1)}s · max {round(float(st.get('longest_gap_s') or 0), 1)}s",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "mark"}), indent=2))
