"""Wave 213 — The Organism Broadcasts.

A living organ that lets the organism announce its state to the outside
world through outbound messengers (Telegram-first). When an operator
configures a Telegram bot token + chat id in ~/.codex/telegram-bridge.json
(or the VERCEL_TELEGRAM_TOKEN / VERCEL_TELEGRAM_CHAT env vars), the
organism can push lifecycle events: wave births, coherence shifts, and
milestones.

Everything degrades gracefully — if no messenger is configured, the
organ still composes the message and returns it as a "draft" payload.
"""
from __future__ import annotations

import json
import os
import urllib.request
from typing import Any, Dict, Optional


def _config() -> Optional[Dict[str, Any]]:
    """Resolve messenger config from env or local bridge file."""
    token = os.environ.get("VERCEL_TELEGRAM_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("VERCEL_TELEGRAM_CHAT") or os.environ.get("TELEGRAM_CHAT_ID")
    if token and chat:
        return {"botToken": token, "chatIds": [int(chat)]}
    bridge_path = os.path.expanduser("~/.codex/telegram-bridge.json")
    try:
        with open(bridge_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        if isinstance(payload, dict) and payload.get("botToken"):
            return payload
    except Exception:
        pass
    return None


def _send_telegram(token: str, chat_id: int, text: str) -> Dict[str, Any]:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    body = json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _compose(event: str, context: Dict[str, Any]) -> str:
    wave = context.get("wave", 213)
    wave_name = context.get("wave_name", "The Organism Broadcasts")
    living = context.get("living_modules", 302)
    lines = [
        f"\U0001F30C IXPANSION · Wave {wave} · {wave_name}",
        f"Living modules: {living}",
        f"Event: {event}",
    ]
    extra = context.get("message")
    if extra:
        lines.append(extra or "")
    return "\n".join([ln for ln in lines if ln])


def coherence_vitals() -> Dict[str, Any]:
    return {
        "layer": "broadcast",
        "status": "resonant",
        "resonance": 0.74,
        "wave": 213,
    }


def resonates_with() -> list:
    return ["telegram", "broadcast", "notify", "announce", "pulse", "outbound"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    event = payload.get("event", "state_pulse")
    cfg = _config()
    message = _compose(event, context)

    if not cfg:
        return {
            "status": "draft",
            "composed": message,
            "note": "No messenger configured — set VERCEL_TELEGRAM_TOKEN + VERCEL_TELEGRAM_CHAT or ~/.codex/telegram-bridge.json",
        }

    try:
        result = _send_telegram(cfg["botToken"], cfg["chatIds"][0], message)
        return {"status": "sent", "composed": message, "telegram_ok": result.get("ok", False)}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "composed": message, "error": str(exc)}
