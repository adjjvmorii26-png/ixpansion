"""Security regression: Telegram broadcast must fail closed without TELEGRAM_BOT_TOKEN.

Proves no network request is made to api.telegram.org when the bot token is absent.
"""
import importlib

import api.telegram_broadcast as tb


def _reload_without_token(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    importlib.reload(tb)
    return tb


def test_bot_token_empty_when_not_configured(monkeypatch):
    module = _reload_without_token(monkeypatch)
    assert module.BOT_TOKEN == ""


def test_no_network_request_without_token(monkeypatch):
    module = _reload_without_token(monkeypatch)

    calls = []
    real_urlopen = module.urllib.request.urlopen

    def _blocking_urlopen(req, *args, **kwargs):
        calls.append(getattr(req, "full_url", req))
        raise AssertionError(
            "telegram_broadcast must not call Telegram without a configured token"
        )

    module.urllib.request.urlopen = _blocking_urlopen
    try:
        result = module._telegram("sendMessage", {"chat_id": "12345", "text": "hi"})
    finally:
        module.urllib.request.urlopen = real_urlopen

    assert result["ok"] is False
    assert "TELEGRAM_BOT_TOKEN" in result["error"]
    assert calls == []


def test_send_vibe_pulse_fails_closed_without_token(monkeypatch):
    module = _reload_without_token(monkeypatch)

    calls = []
    real_urlopen = module.urllib.request.urlopen

    def _blocking_urlopen(req, *args, **kwargs):
        calls.append(getattr(req, "full_url", req))
        raise AssertionError("no Telegram network request without a token")

    module.urllib.request.urlopen = _blocking_urlopen
    module.get_chat_ids = lambda: [12345]
    module._broadcast_state["subscriptions"][12345] = {
        "pulse_types": "all",
        "mood_alerts": True,
        "frequency": "realtime",
    }
    try:
        result = module.send_vibe_pulse({"type": "pulse"}, {"mood": "neutral"})
    finally:
        module.urllib.request.urlopen = real_urlopen

    assert result["status"] == "failed"
    assert result["sent_count"] == 0
    assert result["failed_count"] == 1
    assert calls == []


def test_send_mood_alert_fails_closed_without_token(monkeypatch):
    module = _reload_without_token(monkeypatch)

    calls = []
    real_urlopen = module.urllib.request.urlopen

    def _blocking_urlopen(req, *args, **kwargs):
        calls.append(getattr(req, "full_url", req))
        raise AssertionError("no Telegram network request without a token")

    module.urllib.request.urlopen = _blocking_urlopen
    module.get_chat_ids = lambda: [12345]
    module._broadcast_state["subscriptions"][12345] = {
        "pulse_types": "all",
        "mood_alerts": True,
        "frequency": "realtime",
    }
    try:
        result = module.send_mood_alert({"mood": "neutral"})
    finally:
        module.urllib.request.urlopen = real_urlopen

    assert result["status"] == "failed"
    assert result["sent_count"] == 0
    assert calls == []
