from __future__ import annotations

import importlib
import os
import unittest
from unittest.mock import patch

from api import telegram_broadcast


class TelegramBroadcastTokenTests(unittest.TestCase):
    def test_missing_token_fails_closed_without_network_request(self):
        original_token = telegram_broadcast.BOT_TOKEN
        try:
            with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": ""}):
                importlib.reload(telegram_broadcast)
                self.assertEqual(telegram_broadcast.BOT_TOKEN, "")
                with patch("api.telegram_broadcast.urllib.request.urlopen") as urlopen:
                    result = telegram_broadcast._telegram("getMe", {})
                self.assertEqual(result, {
                    "ok": False,
                    "error": "TELEGRAM_BOT_TOKEN is not configured",
                })
                urlopen.assert_not_called()
        finally:
            telegram_broadcast.BOT_TOKEN = original_token


if __name__ == "__main__":
    unittest.main()
