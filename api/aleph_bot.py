from __future__ import annotations
"""Aleph Bot — SECURITY HOLD.

Full module must be restored per docs/ALEPH_RESTORE.md
Until then, fail closed without leaking tokens.
"""
import os

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()

def _telegram(method: str, params: dict) -> dict:
    if not BOT_TOKEN:
        return {"ok": False, "error": "TELEGRAM_BOT_TOKEN not set — see docs/ALEPH_RESTORE.md"}
    import urllib.parse, urllib.request, json
    url = "https://api.telegram.org/bot" + BOT_TOKEN + "/" + method
    data = urllib.parse.urlencode(params).encode()
    try:
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode() or "{}")
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

def webhook(update: dict) -> dict:
    return {
        "action": "webhook",
        "handled": False,
        "error": "aleph_bot in security hold — restore full module (docs/ALEPH_RESTORE.md)",
    }

def handle_update(update: dict) -> dict:
    return {
        "action": "handle_update",
        "response": "Aleph is in security restore mode. Operator: docs/ALEPH_RESTORE.md",
        "chat_id": 0,
    }
