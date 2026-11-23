import json
import tempfile
import unittest
from pathlib import Path

from squirrel_cache import CacheIntegrityError, SquirrelCache


class SquirrelCacheTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.cache_dir = Path(self.temp.name) / "nuts"
        self.cache = SquirrelCache(self.cache_dir)

    def test_round_trip_and_same_second_writes_do_not_collide(self):
        first = self.cache.hoard("dark_hex", "first")
        second = self.cache.hoard("dark_hex", "second")
        self.assertNotEqual(first, second)
        self.assertEqual(self.cache.retrieve("dark_hex"), ["first", "second"])

    def test_rejects_path_traversal_tags(self):
        for tag in ("../escape", "x/y", "", " space", "x" * 65):
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                self.cache.hoard(tag, "snippet")

    def test_rejects_empty_snippets(self):
        for snippet in ("", "  ", None):
            with self.subTest(snippet=snippet), self.assertRaises(ValueError):
                self.cache.hoard("valid", snippet)

    def test_detects_tampered_cache_file(self):
        self.cache.hoard("integrity", "original")
        manifest = json.loads(self.cache.manifest_path.read_text(encoding="utf-8"))
        target = self.cache_dir / manifest["entries"][0]["file"]
        target.write_text('{"snippet":"tampered"}', encoding="utf-8")
        with self.assertRaisesRegex(CacheIntegrityError, "SHA-256 mismatch"):
            self.cache.retrieve("integrity")

    def test_detects_missing_cache_file(self):
        self.cache.hoard("missing", "original")
        manifest = json.loads(self.cache.manifest_path.read_text(encoding="utf-8"))
        (self.cache_dir / manifest["entries"][0]["file"]).unlink()
        with self.assertRaisesRegex(CacheIntegrityError, "missing cache item"):
            self.cache.retrieve("missing")

    def test_rejects_corrupt_manifest(self):
        self.cache.manifest_path.write_text("{broken", encoding="utf-8")
        with self.assertRaisesRegex(CacheIntegrityError, "cannot read cache manifest"):
            self.cache.retrieve("anything")

    def test_migrates_original_list_manifest(self):
        legacy_file = self.cache_dir / "nut_legacy_1.json"
        legacy_file.write_text(json.dumps({"tag": "legacy", "snippet": "kept", "cached_at": 1}), encoding="utf-8")
        self.cache.manifest_path.write_text(json.dumps([{"tag": "legacy", "file": legacy_file.name}]), encoding="utf-8")
        self.assertEqual(self.cache.retrieve("legacy"), ["kept"])
        migrated = json.loads(self.cache.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(migrated["schema_version"], 1)
        self.assertEqual(migrated["entries"][0]["tag"], "legacy")
        self.assertRegex(migrated["entries"][0]["sha256"], r"^[0-9a-f]{64}$")

    def test_rejects_unsafe_legacy_manifest_path(self):
        self.cache.manifest_path.write_text(json.dumps([{"tag": "x", "file": "../outside.json"}]), encoding="utf-8")
        with self.assertRaisesRegex(CacheIntegrityError, "invalid legacy manifest entry"):
            self.cache.retrieve("x")


if __name__ == "__main__":
    unittest.main()
