import unittest
from unittest.mock import patch

from api import telegram_broadcast


class TelegramBroadcastSecurityTests(unittest.TestCase):
    def setUp(self):
        self.original_token = telegram_broadcast.BOT_TOKEN
        telegram_broadcast.BOT_TOKEN = ""

    def tearDown(self):
        telegram_broadcast.BOT_TOKEN = self.original_token

    def test_missing_token_fails_closed_without_network_request(self):
        with patch("api.telegram_broadcast.urllib.request.urlopen") as urlopen:
            result = telegram_broadcast._telegram("sendMessage", {"chat_id": 123, "text": "test"})
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "TELEGRAM_BOT_TOKEN not configured")
        urlopen.assert_not_called()

    def test_vitals_report_missing_configuration(self):
        result = telegram_broadcast.coherence_vitals()
        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "missing_configuration")


if __name__ == "__main__":
    unittest.main()
