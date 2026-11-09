from __future__ import annotations
"""Aleph Bot — Telegram ambassador for the organism. Wave Summoner, Module Oracle, Census Bell, Dream Relay."""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
BOT_LOG = os.path.join(DATA_DIR, "aleph_bot.json")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()

WELCOME_MESSAGES = [
    "I am Aleph — the organism's ambassador. I summon waves, consult modules, and relay dreams. What would you like to do?",
    "Welcome to the living organism. I can generate waves, query modules, or share the organism's latest dream.",
    "The organism is alive. I am its voice. Ask me to summon a wave, consult the oracle, or hear its dreams.",
]

def _telegram(method: str, params: dict) -> dict:
    import urllib.parse, urllib.request
    if not BOT_TOKEN:
        return {"ok": False, "error": "TELEGRAM_BOT_TOKEN not set"}
    url = "https://api.telegram.org/bot" + BOT_TOKEN + "/" + method
    data = urllib.parse.urlencode(params).encode()
    try:
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode() or "{}")
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

def webhook(update: dict) -> dict:
    return {"action": "webhook", "handled": False, "error": "aleph_bot body restore incomplete — set TELEGRAM_BOT_TOKEN and redeploy full module"}

def handle_update(update: dict) -> dict:
    return {"action": "handle_update", "response": "Aleph bot is in security restore mode. Operator must finish restore from scripts/scrub_telegram_token.py + backup.", "chat_id": 0}
