import json
import os
import unittest
from unittest.mock import patch

from api import off_vercel_store as store


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def read(self):
        return self.payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class OffVercelStoreTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {
            "UPSTASH_REDIS_REST_URL": "https://example.upstash.io",
            "UPSTASH_REDIS_REST_TOKEN": "test-token",
        }, clear=True)
        self.env.start()

    def tearDown(self):
        self.env.stop()

    @patch("api.off_vercel_store.urllib.request.urlopen")
    def test_get_decodes_json_and_url_encodes_key(self, urlopen):
        urlopen.return_value = FakeResponse(b'{"result":"{\\"ok\\":true}"}')
        result = store.get_json("tenant/a b", {})
        self.assertEqual(result, {"ok": True})
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://example.upstash.io/get/tenant%2Fa%20b")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-token")

    @patch("api.off_vercel_store.urllib.request.urlopen")
    def test_set_posts_json_and_checks_ok(self, urlopen):
        urlopen.return_value = FakeResponse(b'{"result":"OK"}')
        self.assertTrue(store.set_json("session:1", {"n": 3}))
        request = urlopen.call_args.args[0]
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.full_url, "https://example.upstash.io/set/session%3A1")
        self.assertEqual(json.loads(request.data), {"n": 3})

    @patch("api.off_vercel_store.urllib.request.urlopen")
    def test_backend_error_is_not_reported_as_missing_key(self, urlopen):
        urlopen.return_value = FakeResponse(b'{"error":"WRONGPASS"}')
        with self.assertRaises(store.StoreError):
            store.get_json("present-but-unavailable", "fallback")

    def test_partial_upstash_configuration_fails_closed(self):
        os.environ.pop("UPSTASH_REDIS_REST_TOKEN")
        with self.assertRaises(store.StoreConfigurationError):
            store.backend()

    def test_invalid_key_rejected(self):
        for key in ("../escape", "tenant/../escape", r"tenant\\..\\escape", "./secret", "tenant/./secret"):
            with self.subTest(key=key):
                with self.assertRaises(ValueError):
                    store.get_json(key, None)

    def test_no_credentials_reports_ephemeral_backend(self):
        os.environ.clear()
        self.assertEqual(store.backend(), "tmp_only")
        self.assertFalse(store.coherence_vitals()["durable"])


if __name__ == "__main__":
    unittest.main()
