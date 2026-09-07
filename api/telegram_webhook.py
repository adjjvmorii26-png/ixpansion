"""Telegram Webhook handler — receives updates from Telegram and routes to aleph_bot."""
from __future__ import annotations
from typing import Any, Dict

def handler(payload: Dict[str, Any] = None, context: Any = None) -> Dict[str, Any]:
    """Handle incoming Telegram update via aleph_bot.webhook."""
    from api.aleph_bot import webhook
    return webhook(payload or {})
