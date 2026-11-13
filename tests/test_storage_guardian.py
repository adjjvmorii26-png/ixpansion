"""Tests for the autonomous storage guardian's safe observation contract."""
import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from api import storage_guardian


class StorageGuardianTests(unittest.TestCase):
    def test_tmp_only_is_degraded_and_never_claims_durability(self):
        with patch.dict(os.environ, {}, clear=True):
            report = storage_guardian.inspect_storage()
        self.assertEqual(report["status"], "DEGRADED")
        self.assertFalse(report["durable_backend_configured"])
        self.assertEqual(report["backend_reachability"], "NOT_PROBED")
        self.assertFalse(report["autonomy"]["may_claim_unverified_durability"])

    def test_partial_upstash_configuration_is_blocked(self):
        env = {"UPSTASH_REDIS_REST_URL": "https://example.upstash.io"}
        with patch.dict(os.environ, env, clear=True):
            report = storage_guardian.inspect_storage()
        self.assertEqual(report["status"], "BLOCKED")
        self.assertEqual(report["backend"], "misconfigured")

    def test_complete_upstash_pair_is_configured_not_proven_reachable(self):
        env = {"UPSTASH_REDIS_REST_URL": "https://example.upstash.io",
               "UPSTASH_REDIS_REST_TOKEN": "not-a-real-token"}
        with patch.dict(os.environ, env, clear=True):
            report = storage_guardian.inspect_storage()
        self.assertEqual(report["status"], "HEALTHY_CONFIGURED")
        self.assertTrue(report["durable_backend_configured"])
        self.assertEqual(report["backend_reachability"], "NOT_PROBED")

    def test_cache_probe_is_read_only_and_reports_integrity(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "cache.sqlite3")
            with sqlite3.connect(path) as db:
                db.execute("CREATE TABLE cache_entries (cache_key TEXT PRIMARY KEY, payload BLOB NOT NULL, expires_at REAL NOT NULL, touched_at REAL NOT NULL, byte_size INTEGER NOT NULL)")
                db.execute("INSERT INTO cache_entries VALUES ('k', '{}', 9999999999, 1, 2)")
            with patch.dict(os.environ, {"IXP_SQUIRREL_CACHE_PATH": path}, clear=True):
                result = storage_guardian._cache_probe()
            self.assertEqual(result["integrity"], "ok")
            self.assertEqual(result["entries"], 1)
            self.assertEqual(result["bytes"], 2)

    def test_report_never_exposes_backend_secrets(self):
        env = {"UPSTASH_REDIS_REST_URL": "https://secret-host.example",
               "UPSTASH_REDIS_REST_TOKEN": "super-secret-token"}
        with patch.dict(os.environ, env, clear=True):
            report = storage_guardian.inspect_storage()
        rendered = str(report)
        self.assertNotIn("super-secret-token", rendered)
        self.assertNotIn("secret-host", rendered)

    def test_maintenance_prunes_only_expired_ephemeral_cache_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "cache.sqlite3")
            with sqlite3.connect(path) as db:
                db.execute("CREATE TABLE cache_entries (cache_key TEXT PRIMARY KEY, payload BLOB NOT NULL, expires_at REAL NOT NULL, touched_at REAL NOT NULL, byte_size INTEGER NOT NULL)")
                db.executemany(
                    "INSERT INTO cache_entries VALUES (?, '{}', ?, 1, 2)",
                    [("expired", 9), ("live", 11)],
                )
            with patch.dict(os.environ, {"IXP_SQUIRREL_CACHE_PATH": path}, clear=True):
                result = storage_guardian.maintain_ephemeral_cache(now=10)
            self.assertEqual(result["action"], "completed")
            self.assertEqual(result["expired_removed"], 1)
            self.assertFalse(result["durable_data_touched"])
            with sqlite3.connect(path) as db:
                keys = [row[0] for row in db.execute("SELECT cache_key FROM cache_entries")]
            self.assertEqual(keys, ["live"])

    def test_maintenance_skips_missing_cache_without_creating_it(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "absent.sqlite3")
            with patch.dict(os.environ, {"IXP_SQUIRREL_CACHE_PATH": path}, clear=True):
                result = storage_guardian.maintain_ephemeral_cache(now=10)
            self.assertEqual(result["action"], "skipped")
            self.assertFalse(os.path.exists(path))


if __name__ == "__main__":
    unittest.main()
