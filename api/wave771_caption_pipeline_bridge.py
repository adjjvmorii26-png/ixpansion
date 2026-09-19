"""Wave 771 — caption_pipeline_bridge.

QUILL silent captions land in content_output as text frames for @CoodingLooop.
No audio. Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "content_output" / "captions"
STATE_FILE = DATA / "wave771_caption_pipeline_bridge.json"
WAVE = 771
NAME = "caption_pipeline_bridge"
MAX_FRAMES = 48

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "exports": 0,
    "last_path": None,
    "status": "idle",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
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
        "module": "wave771_caption_pipeline_bridge",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "exports": int(st.get("exports") or 0),
        "resonance": round(min(1.0, 0.52 + int(st.get("exports") or 0) * 0.01), 4),
        "surface": "silence",
        "channel": "@CoodingLooop",
    }


def resonates_with() -> list:
    return [
        "wave770_copilot_council_pulse",
        "wave768_hush_compass",
        "wave769_void_index",
        "lab.ops.copilots.quill",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {
            **coherence_vitals(),
            "last_path": st.get("last_path"),
            "surface": "silence",
            "audio": False,
        }

    if action == "export":
        frames = req.get("frames") or []
        if isinstance(frames, str):
            frames = [frames]
        if not frames:
            try:
                import sys

                if str(ROOT) not in sys.path:
                    sys.path.insert(0, str(ROOT))
                from lab.ops.copilots.council import run_council

                package = run_council()
                q = (package.get("quill") or {}) if isinstance(package, dict) else {}
                headline = q.get("headline") or "council pulse"
                bullets = q.get("bullets") or []
                frames = [headline] + list(bullets)[:6]
            except Exception:
                frames = ["council silent"]
        lines = [str(f)[:120] for f in frames[:MAX_FRAMES]]
        OUT.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = OUT / f"caption_{stamp}.json"
        package = {
            "channel": "@CoodingLooop",
            "style": "silent_caption_only",
            "audio": False,
            "ts": _now(),
            "frames": [{"t": i * 2, "text": line} for i, line in enumerate(lines)],
        }
        path.write_text(json.dumps(package, indent=2) + "\n")
        st["exports"] = int(st.get("exports") or 0) + 1
        st["last_path"] = str(path.relative_to(ROOT))
        st["status"] = "exported"
        _save(st)
        return {
            **coherence_vitals(),
            "status": "exported",
            "path": st["last_path"],
            "frames": len(lines),
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("exports") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"captions exported {n}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
