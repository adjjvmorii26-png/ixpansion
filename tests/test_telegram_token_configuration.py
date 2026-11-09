from __future__ import annotations

import unittest
from unittest.mock import patch

from api import aleph_bot, telegram_broadcast


class TelegramTokenConfigurationTests(unittest.TestCase):
    def test_aleph_bot_fails_closed_without_token(self):
        with patch.object(aleph_bot, "BOT_TOKEN", ""), patch(
            "urllib.request.urlopen"
        ) as urlopen:
            result = aleph_bot._telegram("getMe", {})
        self.assertEqual(result, {
            "ok": False,
            "error": "TELEGRAM_BOT_TOKEN is not configured",
        })
        urlopen.assert_not_called()

    def test_broadcast_fails_closed_without_token(self):
        with patch.object(telegram_broadcast, "BOT_TOKEN", ""), patch(
            "urllib.request.urlopen"
        ) as urlopen:
            result = telegram_broadcast._telegram("getMe", {})
        self.assertEqual(result, {
            "ok": False,
            "error": "TELEGRAM_BOT_TOKEN is not configured",
        })
        urlopen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
