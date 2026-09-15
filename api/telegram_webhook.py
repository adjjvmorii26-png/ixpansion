"""Telegram Webhook handler — receives updates from Telegram and routes to aleph_bot."""
from __future__ import annotations
from typing import Any, Dict

def handler(payload: Dict[str, Any] = None, context: Any = None) -> Dict[str, Any]:
    """Handle incoming Telegram update via aleph_bot.webhook."""
    from api.aleph_bot import webhook
    return webhook(payload or {})


def coherence_vitals():
    return {
        "module": "telegram_webhook",
        "ok": True,
        "status": "active",
    }

def resonates_with():
    return ['organism_core', 'coherence_validator', 'consensus_bloom', 'council_oracle', 'causality_weave']

