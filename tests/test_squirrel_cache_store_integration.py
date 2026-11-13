import os
import tempfile
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


class SquirrelCacheStoreIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {
            "UPSTASH_REDIS_REST_URL": "https://example.upstash.io",
            "UPSTASH_REDIS_REST_TOKEN": "test-token",
            "IXP_SQUIRREL_CACHE_PATH": os.path.join(self.tmp.name, "cache.sqlite3"),
        }, clear=True)
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    @patch("api.off_vercel_store.urllib.request.urlopen")
    def test_read_through_cache_avoids_second_remote_read(self, urlopen):
        urlopen.return_value = FakeResponse(b'{"result":"{\\"healthy\\":true}"}')
        first = store.get_json("health", {}, cache_ttl=30)
        second = store.get_json("health", {}, cache_ttl=30)
        self.assertEqual(first, {"healthy": True})
        self.assertEqual(second, {"healthy": True})
        self.assertEqual(urlopen.call_count, 1)

    @patch("api.off_vercel_store.urllib.request.urlopen")
    def test_successful_remote_write_populates_cache(self, urlopen):
        urlopen.return_value = FakeResponse(b'{"result":"OK"}')
        value = {"revision": 7}
        self.assertTrue(store.set_json("manifest", value, cache_ttl=30))
        self.assertEqual(store.get_json("manifest", {}, cache_ttl=30), value)
        self.assertEqual(urlopen.call_count, 1)

    @patch("api.off_vercel_store.urllib.request.urlopen")
    def test_cache_is_opt_in_by_default(self, urlopen):
        urlopen.side_effect = [
            FakeResponse(b'{"result":"{\\"n\\":1}"}'),
            FakeResponse(b'{"result":"{\\"n\\":2}"}'),
        ]
        self.assertEqual(store.get_json("uncached", {}, cache_ttl=0), {"n": 1})
        self.assertEqual(store.get_json("uncached", {}, cache_ttl=0), {"n": 2})
        self.assertEqual(urlopen.call_count, 2)


if __name__ == "__main__":
    unittest.main()
