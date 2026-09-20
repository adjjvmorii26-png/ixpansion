"""Wave 783 — hitl_publish_gate.

Human-in-the-loop gate before wave/caption publish (mesh-HITL metaphor).
Default: hold until approve; auto-deny risky antimeme scores if provided.

Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave783_hitl_publish_gate.json"
WAVE = 783
NAME = "hitl_publish_gate"
MAX_PENDING = 32

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "pending": [],
    "decisions": 0,
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
        "module": "wave783_hitl_publish_gate",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "pending": len(st.get("pending") or []),
        "decisions": int(st.get("decisions") or 0),
        "resonance": round(min(1.0, 0.5 + int(st.get("decisions") or 0) * 0.01), 4),
        "surface": "silence",
        "default_policy": "hold_until_approve",
    }


def resonates_with() -> list:
    return [
        "wave778_antimeme_caption_guard",
        "wave771_caption_pipeline_bridge",
        "wave776_merge_readiness_score",
        "wave782_dream_share_bus",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {
            **coherence_vitals(),
            "queue": [p.get("id") for p in (st.get("pending") or [])],
            "audio": False,
            "surface": "silence",
        }

    if action == "submit":
        label = str(req.get("label") or req.get("topic") or "item")[:64]
        risk = req.get("risk_score")
        try:
            risk_f = float(risk) if risk is not None else 0.0
        except (TypeError, ValueError):
            risk_f = 0.0
        risk_f = max(0.0, min(1.0, risk_f))
        if risk_f >= 0.45:
            st["decisions"] = int(st.get("decisions") or 0) + 1
            st["status"] = "auto_denied"
            _save(st)
            return {
                **coherence_vitals(),
                "status": "denied",
                "reason": "auto_risk_threshold",
                "risk_score": risk_f,
                "payload": None,
                "audio": False,
                "surface": "silence",
            }
        pid = f"hold-{int(st.get('decisions') or 0) + len(st.get('pending') or []) + 1}"
        item = {"id": pid, "label": label, "risk_score": risk_f, "ts": _now()}
        pending = list(st.get("pending") or [])
        pending.append(item)
        st["pending"] = pending[-MAX_PENDING:]
        st["status"] = "holding"
        _save(st)
        return {
            **coherence_vitals(),
            "status": "holding",
            "id": pid,
            "label": label,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action in ("approve", "deny"):
        pid = str(req.get("id") or "")
        pending = list(st.get("pending") or [])
        found = None
        rest = []
        for p in pending:
            if p.get("id") == pid and found is None:
                found = p
            else:
                rest.append(p)
        if not found and pending and not pid:
            found = pending[0]
            rest = pending[1:]
        if not found:
            return {**coherence_vitals(), "status": "not_found", "audio": False}
        st["pending"] = rest
        st["decisions"] = int(st.get("decisions") or 0) + 1
        st["status"] = "approved" if action == "approve" else "denied"
        st["last_id"] = found.get("id")
        _save(st)
        return {
            **coherence_vitals(),
            "status": st["status"],
            "id": found.get("id"),
            "label": found.get("label"),
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("decisions") or 0)
        p = len(st.get("pending") or [])
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"hitl decisions {n} · pending {p}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "submit", "label": "demo"}), indent=2))
