"""Contract tests for IXPANSION's Upstash atomic storage adapter."""
import json
import os
import unittest
from unittest.mock import patch

from api import atomic_store


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload
    def read(self):
        return self.payload
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False


class AtomicStoreTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {
            "UPSTASH_REDIS_REST_URL": "https://example.upstash.io",
            "UPSTASH_REDIS_REST_TOKEN": "test-token",
        }, clear=True)
        self.env.start()

    def tearDown(self):
        self.env.stop()

    @patch("api.off_vercel_store.urllib.request.urlopen")
    def test_increment_uses_atomic_incrby(self, urlopen):
        urlopen.return_value = FakeResponse(b'{"result":7}')
        self.assertEqual(atomic_store.get_atomic_store().increment("usage:user-1", 3), 7)
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://example.upstash.io/")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-token")
        self.assertEqual(json.loads(request.data), ["INCRBY", "ixpansion:atomic:usage:user-1", 3])

    @patch("api.off_vercel_store.urllib.request.urlopen")
    def test_compare_and_swap_uses_server_side_eval(self, urlopen):
        urlopen.return_value = FakeResponse(b'{"result":1}')
        store = atomic_store.get_atomic_store()
        self.assertTrue(store.compare_and_swap("state:one", {"version": 1}, {"version": 2}))
        command = json.loads(urlopen.call_args.args[0].data)
        self.assertEqual(command[0], "EVAL")
        self.assertEqual(command[2], 1)
        self.assertEqual(command[3], "ixpansion:atomic:state:one")
        self.assertIn("redis.call('SET'", command[1])

    @patch("api.off_vercel_store.urllib.request.urlopen")
    def test_compare_and_swap_can_create_only_when_missing(self, urlopen):
        urlopen.return_value = FakeResponse(b'{"result":0}')
        store = atomic_store.get_atomic_store()
        self.assertFalse(store.compare_and_swap("state:new", None, {"version": 1}, expect_missing=True))
        command = json.loads(urlopen.call_args.args[0].data)
        self.assertEqual(command[4], "MISSING")

    @patch("api.off_vercel_store.urllib.request.urlopen")
    def test_append_event_supports_idempotent_retries(self, urlopen):
        urlopen.return_value = FakeResponse(b'{"result":"1712345678901-0"}')
        store = atomic_store.get_atomic_store()
        event_id = store.append_event(
            "auth-audit", {"action": "login"}, idempotency_key="request-123"
        )
        self.assertEqual(event_id, "1712345678901-0")
        command = json.loads(urlopen.call_args.args[0].data)
        self.assertEqual(command[0], "EVAL")
        self.assertEqual(command[2], 2)
        self.assertIn("XADD", command[1])
        self.assertEqual(command[-1], 86400)

    def test_generic_http_backend_is_not_assumed_atomic(self):
        with patch.dict(os.environ, {
            "IXP_STATE_HTTP_GET": "https://example.invalid/get/{key}",
            "IXP_STATE_HTTP_PUT": "https://example.invalid/put/{key}",
        }, clear=True):
            with self.assertRaises(atomic_store.AtomicStoreCapabilityError):
                atomic_store.get_atomic_store()

    def test_ephemeral_backend_is_not_accepted(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(atomic_store.AtomicStoreCapabilityError):
                atomic_store.get_atomic_store()

    def test_invalid_increment_amount_rejected(self):
        store = atomic_store.get_atomic_store()
        with self.assertRaises(TypeError):
            store.increment("counter", True)


if __name__ == "__main__":
    unittest.main()
