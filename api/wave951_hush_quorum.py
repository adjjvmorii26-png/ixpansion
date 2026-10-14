"""Wave 951 — hush_quorum.

Silent quorum check over hush/witness tokens. Returns only a binary token.
Does not replay organs. Payload stays empty. Silence is the product surface.
Lab organ only. Lab gates ≠ ALEPH CI. Compression is memory.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave951_hush_quorum.json"
WAVE = 951
NAME = "hush_quorum"
QUORUM = 0.66

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "checks": 0,
    "last_token": "",
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


def _quorum_token(tokens: list) -> str:
    """Binary silent token: 1 if support >= quorum else 0, hashed."""
    clean = [str(t)[:32] for t in tokens if t][:8]
    if not clean:
        return "0"
    # Deterministic support: unique hashes weighted equally
    unique = len(set(clean))
    support = unique / max(1, len(clean))
    bit = "1" if support >= QUORUM else "0"
    raw = f"{bit}|{len(clean)}|{''.join(sorted(set(clean)))}"
    return hashlib.sha256(raw.encode()).hexdigest()[:8]


def coherence_vitals() -> dict:
    st = _load()
    checks = int(st.get("checks") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave951_hush_quorum",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "checks": checks,
        "quorum": QUORUM,
        "resonance": round(min(1.0, 0.60 + checks * 0.005), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave950_hush_margin",
        "wave949_council_witness",
        "wave675_consensus_bloom",
        "wave941_hush_fold",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "quorum":
        tokens = req.get("tokens") or req.get("hush") or []
        if isinstance(tokens, str):
            tokens = [t.strip() for t in tokens.split(",") if t.strip()]
        token = _quorum_token(tokens)
        st["checks"] = int(st.get("checks") or 0) + 1
        st["last_token"] = token
        st["status"] = "quorumed"
        st["last_ts"] = _now()
        st["n"] = len(tokens) if isinstance(tokens, list) else 0
        _save(st)
        return {
            **coherence_vitals(),
            "status": "quorumed",
            "token": token,
            "caption": f"hush quorum · {token}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        t = st.get("last_token") or ""
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"silent quorum {t}" if t else "silent quorum idle",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "quorum", "tokens": ["abc", "def", "abc"]}), indent=2))
