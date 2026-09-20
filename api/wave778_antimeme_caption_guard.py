"""Wave 778 — antimeme_caption_guard.

Score silent caption frames for antimemetic leakage risk.
Inspired by antimemetic-architecton — protect the silence surface.

Silence is the product surface. Lab gates ≠ ALEPH CI. No audio.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave778_antimeme_caption_guard.json"
WAVE = 778
NAME = "antimeme_caption_guard"

RISK_PATTERNS = [
    (r"\b(password|secret|token|api[_-]?key)\b", 0.35, "credential_lexeme"),
    (r"https?://\S+", 0.15, "url_leak"),
    (r"\b[A-Za-z0-9+/]{32,}={0,2}\b", 0.25, "blob_like"),
    (r"\b(must know|reveal|expose|decrypt)\b", 0.2, "force_reveal"),
    (r"\{[^{}]{20,}\}", 0.15, "jsonish"),
]

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "scans": 0,
    "blocked": 0,
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


def _score_text(text: str) -> dict:
    text = text or ""
    hits = []
    score = 0.0
    for pat, w, label in RISK_PATTERNS:
        if re.search(pat, text, re.I):
            hits.append(label)
            score += w
    if len(text) > 160:
        score += 0.1
        hits.append("overlong")
    score = min(1.0, round(score, 4))
    if score >= 0.45:
        verdict = "block"
    elif score >= 0.2:
        verdict = "trim"
    else:
        verdict = "pass"
    return {"score": score, "hits": hits, "verdict": verdict}


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave778_antimeme_caption_guard",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "scans": int(st.get("scans") or 0),
        "blocked": int(st.get("blocked") or 0),
        "resonance": round(min(1.0, 0.52 + int(st.get("scans") or 0) * 0.008), 4),
        "surface": "silence",
        "channel": "@CoodingLooop",
    }


def resonates_with() -> list:
    return [
        "wave771_caption_pipeline_bridge",
        "wave769_void_index",
        "wave768_hush_compass",
        "wave775_constellation_affinity",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "scan":
        text = str(req.get("text") or req.get("caption") or "")
        result = _score_text(text)
        st["scans"] = int(st.get("scans") or 0) + 1
        if result["verdict"] == "block":
            st["blocked"] = int(st.get("blocked") or 0) + 1
        st["status"] = "scanned"
        st["last_verdict"] = result["verdict"]
        st["last_ts"] = _now()
        _save(st)
        safe = text[:80] + ("…" if len(text) > 80 else "") if result["verdict"] != "block" else ""
        return {
            **coherence_vitals(),
            "status": "scanned",
            **result,
            "safe_preview": safe if result["verdict"] != "block" else None,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        b = int(st.get("blocked") or 0)
        n = int(st.get("scans") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"antimeme scans {n} · blocked {b}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "scan", "text": "council green · silence holds"}), indent=2))
