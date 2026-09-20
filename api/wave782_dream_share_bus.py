"""Wave 782 — dream_share_bus.

Quiet multi-perspective briefs (oracle-engine metaphor): several viewpoints
fold into one silent packet for council/caption — no audio.

Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave782_dream_share_bus.json"
WAVE = 782
NAME = "dream_share_bus"
DEFAULT_VOICES = ("aegis", "helix", "quill", "edge")

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "dreams": 0,
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


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave782_dream_share_bus",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "dreams": int(st.get("dreams") or 0),
        "resonance": round(min(1.0, 0.5 + int(st.get("dreams") or 0) * 0.01), 4),
        "surface": "silence",
        "voices": list(DEFAULT_VOICES),
    }


def resonates_with() -> list:
    return [
        "wave770_copilot_council_pulse",
        "wave771_caption_pipeline_bridge",
        "wave778_antimeme_caption_guard",
        "wave780_pentaxis_projection",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "share":
        topic = str(req.get("topic") or "pulse")[:80]
        perspectives = req.get("perspectives")
        if not isinstance(perspectives, dict):
            perspectives = {
                "aegis": "gates hold",
                "helix": "grow next free wave",
                "quill": "caption only",
                "edge": "dual-track",
            }
        lines = []
        for voice in DEFAULT_VOICES:
            if voice in perspectives:
                lines.append(f"{voice}: {str(perspectives[voice])[:60]}")
        for k, v in perspectives.items():
            if k not in DEFAULT_VOICES:
                lines.append(f"{k}: {str(v)[:60]}")
        packet = {
            "topic": topic,
            "lines": lines[:12],
            "ts": _now(),
            "audio": False,
            "surface": "silence",
        }
        st["dreams"] = int(st.get("dreams") or 0) + 1
        st["status"] = "shared"
        st["last_topic"] = topic
        st["last_line_count"] = len(packet["lines"])
        _save(st)
        return {
            **coherence_vitals(),
            "status": "shared",
            "packet": packet,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("dreams") or 0)
        t = st.get("last_topic") or "-"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"dreams {n} · last {t}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "share", "topic": "scan"}), indent=2))
