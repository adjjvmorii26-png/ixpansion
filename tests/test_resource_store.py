import unittest

from resource_store import ResourceStore


class ResourceStoreTests(unittest.TestCase):
    def test_resource_passport_round_trips_and_lists_without_raw_text(self):
        store = ResourceStore(":memory:")
        saved = store.save(
            "resource-1",
            source_url="https://docs.example/page",
            title="Docs",
            links=["https://docs.example/next"],
            artifact={"chunks": ["redacted text"], "redacted": True},
        )

        self.assertEqual(saved["resource_id"], "resource-1")
        self.assertEqual(saved["artifact"]["chunks"], ["redacted text"])
        self.assertEqual(store.list()[0]["source_url"], "https://docs.example/page")
        store.close()

    def test_missing_resource_is_not_found(self):
        store = ResourceStore(":memory:")
        with self.assertRaises(KeyError):
            store.get("missing")
        store.close()