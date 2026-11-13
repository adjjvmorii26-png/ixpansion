import os
import unittest
from unittest.mock import patch

from api import telegram_broadcast


class FakeResponse:
    def read(self):
        return b'{"ok":true}'

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class TelegramCredentialTests(unittest.TestCase):
    @patch.dict(os.environ, {}, clear=True)
    @patch("api.telegram_broadcast.urllib.request.urlopen")
    def test_missing_token_fails_closed_without_network_request(self, urlopen):
        result = telegram_broadcast._telegram("sendMessage", {"chat_id": 1})
        self.assertFalse(result["ok"])
        self.assertIn("not configured", result["error"])
        urlopen.assert_not_called()

    @patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test-token"}, clear=True)
    @patch("api.telegram_broadcast.urllib.request.urlopen")
    def test_token_is_read_from_environment_at_call_time(self, urlopen):
        urlopen.return_value = FakeResponse()
        result = telegram_broadcast._telegram("sendMessage", {"chat_id": 1})
        self.assertTrue(result["ok"])
        request = urlopen.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "https://api.telegram.org/bottest-token/sendMessage",
        )
        self.assertEqual(result, {"ok": True})


if __name__ == "__main__":
    unittest.main()
