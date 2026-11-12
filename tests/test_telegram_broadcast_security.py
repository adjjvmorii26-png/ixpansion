"""Security contract tests for Telegram broadcast configuration."""

from api import telegram_broadcast


def test_telegram_api_fails_closed_without_token(monkeypatch):
    monkeypatch.setattr(telegram_broadcast, "BOT_TOKEN", None)

    def unexpected_network_call(*args, **kwargs):
        raise AssertionError("network must not be called without a bot token")

    monkeypatch.setattr(telegram_broadcast.urllib.request, "urlopen", unexpected_network_call)
    result = telegram_broadcast._telegram("sendMessage", {"chat_id": 123, "text": "test"})

    assert result == {
        "ok": False,
        "error": "Telegram bot token is not configured",
    }
