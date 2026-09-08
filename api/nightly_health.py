"""Wave 512: Nightly Health — scheduled health check via Vercel cron.

Runs every night, checks the organism's vital signs, and posts a
summary to Telegram. Also serves as a manual health check endpoint.

Doctrine: The organism checks itself while the world sleeps.
"""
from __future__ import annotations
import json
import os
import time
from typing import Any, Dict


def handler(request: Any = None, context: Any = None) -> Dict[str, Any]:
    from api.organism_pulse import handler as pulse_handler
    pulse = pulse_handler()
    checks = pulse.get("checks", {})
    summary = {
        "action": "nightly_health",
        "timestamp": time.time(),
        "health": pulse.get("health", "unknown"),
        "organs": checks.get("organs", "?"),
        "mood": checks.get("mood", {}).get("word", "?"),
        "citizens": checks.get("citizens", "?"),
        "council_sessions": checks.get("council_sessions", "?"),
        "confluence_messages": checks.get("confluence_messages", "?"),
        "confluence_agents": checks.get("confluence_agents", "?"),
        "total_visits": checks.get("total_visits", "?"),
        "errors": pulse.get("errors", 0),
    }
    try:
        from api.cythara_broadcast import send_telegram
        msg = (
            f"Nightly Health Check — {summary['health']}\n"
            f"Organs: {summary['organs']} | Citizens: {summary['citizens']}\n"
            f"Mood: {summary['mood']} | Sessions: {summary['council_sessions']}\n"
            f"Messages: {summary['confluence_messages']} | Visits: {summary['total_visits']}\n"
            f"Errors: {summary['errors']}"
        )
        result = send_telegram(msg)
        summary["telegram"] = result.get("status", "no chat ids")
    except Exception as exc:
        summary["telegram"] = f"error: {exc}"
    return summary
