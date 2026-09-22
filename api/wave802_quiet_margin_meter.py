"""Wave 802 — quiet_margin_meter.

Measure quiet margin from text uniqueness density (silence-first observability).
Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave802_quiet_margin_meter.json"
WAVE = 802
NAME = "quiet_margin_meter"

DEFAULT = {"wave": WAVE, "name": NAME, "measures": 0, "status": "idle"}


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


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave802_quiet_margin_meter",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "measures": int(st.get("measures") or 0),
        "last_margin": st.get("last_margin"),
        "resonance": round(min(1.0, 0.5 + int(st.get("measures") or 0) * 0.01), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave778_antimeme_caption_guard",
        "wave795_residual_echo_filter",
        "wave785_silent_publish_orchestrator",
        "wave771_caption_pipeline_bridge",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "measure":
        text = str(req.get("text") or "")
        n = len(text)
        if n == 0:
            margin = 1.0
        else:
            uniq = len(set(text.lower()))
            density = min(1.0, uniq / max(1, min(n, 40)))
            margin = round(1.0 - density, 4)
        band = "deep" if margin >= 0.7 else ("soft" if margin >= 0.4 else "thin")
        st["measures"] = int(st.get("measures") or 0) + 1
        st["last_margin"] = margin
        st["status"] = "measured"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "measured",
            "margin": margin,
            "band": band,
            "advice": "prefer silence" if band == "thin" else "caption ok",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("measures") or 0)
        m = st.get("last_margin")
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"quiet margin measures {n}" + (f" · {m}" if m is not None else ""),
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "measure", "text": "hush"}), indent=2))
