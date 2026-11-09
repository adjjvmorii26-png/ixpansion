"""Central env secrets — never hardcode tokens."""
from __future__ import annotations
import os

def telegram_bot_token() -> str:
    return (os.environ.get("TELEGRAM_BOT_TOKEN") or "").strip()

def require_telegram_token() -> str:
    tok = telegram_bot_token()
    if not tok:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    return tok
