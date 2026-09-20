"""Wave 786 — echotide_caption_pace.

Echotide crest metaphor: timing offsets for silent caption frames.
No audio. Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave786_echotide_caption_pace.json"
WAVE = 786
NAME = "echotide_caption_pace"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "paces": 0,
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
        "module": "wave786_echotide_caption_pace",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "paces": int(st.get("paces") or 0),
        "resonance": round(min(1.0, 0.5 + int(st.get("paces") or 0) * 0.01), 4),
        "surface": "silence",
        "channel": "@CoodingLooop",
    }


def resonates_with() -> list:
    return [
        "wave771_caption_pipeline_bridge",
        "wave785_silent_publish_orchestrator",
        "wave778_antimeme_caption_guard",
        "wave782_dream_share_bus",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "pace":
        frames = req.get("frames") or []
        if isinstance(frames, str):
            frames = [frames]
        frames = [str(f)[:120] for f in frames[:24]]
        try:
            base = float(req.get("base_sec") if req.get("base_sec") is not None else 2.0)
        except (TypeError, ValueError):
            base = 2.0
        base = max(0.5, min(8.0, base))
        timed = []
        t = 0.0
        for i, text in enumerate(frames):
            dur = base * (1.15 if i % 2 == 0 else 0.85)
            timed.append({"t": round(t, 2), "dur": round(dur, 2), "text": text})
            t += dur
        st["paces"] = int(st.get("paces") or 0) + 1
        st["status"] = "paced"
        st["last_total"] = round(t, 2)
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "paced",
            "frames": timed,
            "total_sec": round(t, 2),
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("paces") or 0)
        tot = st.get("last_total")
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"tide paces {n}" + (f" · {tot}s" if tot is not None else ""),
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "pace", "frames": ["hook", "core", "cta"]}), indent=2))
