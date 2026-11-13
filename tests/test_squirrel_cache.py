import multiprocessing
import tempfile
import unittest
from pathlib import Path

from api.squirrel_cache import SquirrelCache


def _cache_writer(path, start, count):
    cache = SquirrelCache(path=path, max_entries=1000, max_bytes=1_000_000)
    for index in range(count):
        cache.put(f"worker:{start}:{index}", {"value": index}, ttl=60)


class SquirrelCacheTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.tmp.name) / "cache.sqlite3")
        self.cache = SquirrelCache(self.path, max_entries=10, max_bytes=1024)

    def tearDown(self):
        self.tmp.cleanup()

    def test_ttl_expiration(self):
        self.cache.put("alpha", {"n": 1}, ttl=5, now=100)
        self.assertEqual(self.cache.get("alpha", now=104), (True, {"n": 1}))
        self.assertEqual(self.cache.get("alpha", now=105), (False, None))

    def test_entry_and_byte_limits(self):
        for index in range(20):
            self.cache.put(f"k{index}", "x" * 40, ttl=60, now=100 + index)
        stats = self.cache.stats()
        self.assertLessEqual(stats["entries"], 10)
        self.assertLessEqual(stats["bytes"], 1024)

    def test_oversized_value_is_not_cached(self):
        self.assertFalse(self.cache.put("huge", "x" * 2048, ttl=60))
        self.assertEqual(self.cache.get("huge"), (False, None))

    def test_cache_is_explicitly_non_authoritative(self):
        stats = self.cache.stats()
        self.assertFalse(stats["durable"])
        self.assertFalse(stats["authority"])

    def test_concurrent_process_writes(self):
        workers = [
            multiprocessing.Process(target=_cache_writer, args=(self.path, i, 20))
            for i in range(3)
        ]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join(10)
            self.assertEqual(worker.exitcode, 0)
        self.assertEqual(self.cache.stats()["entries"], 60)

    def test_failed_transaction_rolls_back(self):
        self.cache.put("stable", {"v": 1}, ttl=60)
        with self.assertRaises(Exception):
            with self.cache._connect() as db:
                db.execute("BEGIN IMMEDIATE")
                db.execute("INSERT INTO cache_entries VALUES (?, ?, ?, ?, ?)",
                           ("broken", b"{}", 9999999999, 1, 2))
                db.execute("INSERT INTO missing_table VALUES (1)")
                db.execute("COMMIT")
        self.assertEqual(self.cache.get("stable"), (True, {"v": 1}))
        self.assertEqual(self.cache.get("broken"), (False, None))


if __name__ == "__main__":
    unittest.main()
