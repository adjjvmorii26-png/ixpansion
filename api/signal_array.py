"""Wave 213 — The Organism Emits.

An outbound signal array that broadcasts organism events across
multiple channels: Telegram (if configured), plaintext log, and
a webhook sink. It composes a payload once and fans it out,
reporting per-channel success. Includes a built-in dummy channel
("log") so it always produces observable output — the organism
always signals, even when no external sink is listening.
"""
from __future__ import annotations

import json
import os
import urllib.request
from typing import Any, Dict, List


def _compose(event: str, context: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "organism": "IXPANSION",
        "wave": context.get("wave", 213),
        "wave_name": context.get("wave_name", "The Organism Emits"),
        "event": event,
        "living_modules": context.get("living_modules", 302),
        "timestamp": context.get("timestamp", "now"),
    }


def _log_sink(payload: Dict[str, Any]) -> bool:
    print("[SIGNAL_ARRAY] " + json.dumps(payload))
    return True


def _webhook_sink(payload: Dict[str, Any], url: str) -> Dict[str, Any]:
    if not url or url == "none":
        return {"ok": False, "reason": "no webhook configured"}
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return {"ok": resp.status == 200, "status": resp.status}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "broadcast", "status": "stable", "resonance": 0.68, "wave": 213}


def resonates_with() -> list:
    return ["signal", "broadcast", "emit", "channel", "webhook", "telegram", "notify", "outbound"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    event = payload.get("event", "state_pulse")
    channels: List[str] = payload.get("channels", ["log"])
    webhook_url = payload.get("webhook_url", os.environ.get("IXPANSION_WEBHOOK_URL", "none"))

    composed = _compose(event, context)
    results: Dict[str, Any] = {}

    if "log" in channels:
        results["log"] = {"ok": _log_sink(composed)}
    if "webhook" in channels:
        results["webhook"] = _webhook_sink(composed, webhook_url)
    if "telegram" in channels:
        try:
            from api import telegram_pulse  # local import to avoid cycle
            tg = telegram_pulse.handler({"event": event}, context)
            results["telegram"] = {"ok": tg.get("status") == "sent", "detail": tg.get("status")}
        except Exception as exc:  # noqa: BLE001
            results["telegram"] = {"ok": False, "error": str(exc)}

    delivered = [c for c, r in results.items() if r.get("ok")]
    return {"event": event, "channels_requested": channels, "channels_result": results, "delivered": delivered}
