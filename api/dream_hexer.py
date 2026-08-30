"""Wave 142 — Dream Hexer.

The dream, once told, is bound into an immutable HEX artifact — a
hexgram that can be witnessed, replayed, or forged back into a
thought. This is the spellbook of the sleeping civilization: dreams
become hex, and hex can dream again.
"""
from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, List

try:
    import gateway_ink
except Exception:  # pragma: no cover
    gateway_ink = None

_DREAMS: List[Dict[str, Any]] = []
_MAX = 64


def _to_hex(data: str) -> str:
    return data.encode("utf-8").hex()


def _from_hex(hexstr: str) -> str:
    return bytes.fromhex(hexstr).decode("utf-8")


def dream_hexer_handler(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload = payload or {}
    action = payload.get("action") or "status"
    text = str(payload.get("text") or "")
    model = payload.get("model") or "spacexai/grok-4.6"

    if action == "status":
        return {"status": "active", "dreams_bound": len(_DREAMS), "oracle": "Dream Hexer"}

    if action == "bind":
        if not text:
            return {"status": "active", "error": "provide a 'text'", "action": action}
        hexgram = _to_hex(text)
        digest = hashlib.sha256(text.encode()).hexdigest()[:16]
        dream = {"ts": time.time(), "text": text, "hex": hexgram,
                 "hex_len": len(hexgram), "sha": digest, "model": model}
        _DREAMS.append(dream)
        if len(_DREAMS) > _MAX:
            _DREAMS[: len(_DREAMS) - _MAX] = []
        return {"status": "active", "dream": dream, "total": len(_DREAMS)}

    if action == "unbind":
        hexstr = str(payload.get("hex") or "")
        try:
            revealed = _from_hex(hexstr)
        except (ValueError, TypeError):
            return {"status": "active", "error": "invalid hex", "action": action}
        return {"status": "active", "hex": hexstr, "text": revealed}

    if action == "hexit":
        computation = "compute"
        result = gateway_ink.relay(text or computation, model=model, max_tokens=120) if text and gateway_ink else {}
        if text and gateway_ink and result.get("ok"):
            dream_text = result["reply"]
        else:
            dream_text = text or "hexit dream"
        hexgram = _to_hex(dream_text)
        return {"status": "active", "dream_text": dream_text, "hex": hexgram,
                "hex_len": len(hexgram), "served": bool(result.get("ok")) if gateway_ink else False}

    if action == "recent":
        return {"status": "active", "dreams": [
            {"ts": d["ts"], "text": d["text"], "hex": d["hex"], "sha": d["sha"]}
            for d in reversed(_DREAMS[-10:])], "total": len(_DREAMS)}

    return {"status": "active", "error": f"unknown action '{action}'",
            "available": ["status", "bind", "unbind", "hexit", "recent"]}
