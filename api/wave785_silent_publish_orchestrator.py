"""Wave 785 — silent_publish_orchestrator.

One call: antimeme scan → HITL submit/auto-deny → optional caption export.
No audio. Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave785_silent_publish_orchestrator.json"
WAVE = 785
NAME = "silent_publish_orchestrator"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "runs": 0,
    "last_outcome": None,
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


def _import_api(mod: str):
    api = ROOT / "api"
    if str(api) not in sys.path:
        sys.path.insert(0, str(api))
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    return __import__(mod)


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave785_silent_publish_orchestrator",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "runs": int(st.get("runs") or 0),
        "last_outcome": st.get("last_outcome"),
        "resonance": round(min(1.0, 0.5 + int(st.get("runs") or 0) * 0.01), 4),
        "surface": "silence",
        "pipeline": ["antimeme", "hitl", "caption_optional"],
    }


def resonates_with() -> list:
    return [
        "wave778_antimeme_caption_guard",
        "wave783_hitl_publish_gate",
        "wave771_caption_pipeline_bridge",
        "wave782_dream_share_bus",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "publish":
        text = str(req.get("text") or req.get("caption") or "council silent")
        auto_approve = bool(req.get("auto_approve"))
        steps = {}
        try:
            guard = _import_api("wave778_antimeme_caption_guard")
            scan = guard.handler({"action": "scan", "text": text})
            steps["antimeme"] = {"verdict": scan.get("verdict"), "score": scan.get("score")}
            risk = float(scan.get("score") or 0)
            if scan.get("verdict") == "block":
                st["runs"] = int(st.get("runs") or 0) + 1
                st["last_outcome"] = "blocked_antimeme"
                st["status"] = "blocked"
                _save(st)
                return {
                    **coherence_vitals(),
                    "status": "blocked",
                    "steps": steps,
                    "payload": None,
                    "audio": False,
                    "surface": "silence",
                }
        except Exception as e:
            steps["antimeme"] = {"error": str(e)[:80]}
            risk = 0.0

        try:
            hitl = _import_api("wave783_hitl_publish_gate")
            sub = hitl.handler({"action": "submit", "label": text[:48], "risk_score": risk})
            steps["hitl"] = {"status": sub.get("status"), "id": sub.get("id")}
            if sub.get("status") == "denied":
                st["runs"] = int(st.get("runs") or 0) + 1
                st["last_outcome"] = "denied_hitl"
                st["status"] = "denied"
                _save(st)
                return {
                    **coherence_vitals(),
                    "status": "denied",
                    "steps": steps,
                    "payload": None,
                    "audio": False,
                    "surface": "silence",
                }
            if sub.get("status") == "holding" and auto_approve and sub.get("id"):
                ap = hitl.handler({"action": "approve", "id": sub["id"]})
                steps["hitl_approve"] = ap.get("status")
            elif sub.get("status") == "holding" and not auto_approve:
                st["runs"] = int(st.get("runs") or 0) + 1
                st["last_outcome"] = "holding"
                st["status"] = "holding"
                _save(st)
                return {
                    **coherence_vitals(),
                    "status": "holding",
                    "steps": steps,
                    "payload": None,
                    "audio": False,
                    "surface": "silence",
                }
        except Exception as e:
            steps["hitl"] = {"error": str(e)[:80]}

        if req.get("export"):
            try:
                cap = _import_api("wave771_caption_pipeline_bridge")
                frames = req.get("frames") or [text]
                ex = cap.handler({"action": "export", "frames": frames})
                steps["export"] = {"status": ex.get("status"), "path": ex.get("path")}
            except Exception as e:
                steps["export"] = {"error": str(e)[:80]}

        st["runs"] = int(st.get("runs") or 0) + 1
        st["last_outcome"] = "published"
        st["status"] = "published"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "published",
            "steps": steps,
            "caption": text[:120],
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("runs") or 0)
        o = st.get("last_outcome") or "-"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"publish runs {n} · last {o}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "publish", "text": "hush holds", "auto_approve": True}), indent=2))
