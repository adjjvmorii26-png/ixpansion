import copy
import json
import tempfile
import unittest
from pathlib import Path

from library_validator import (
    build_index,
    find_contradictions,
    load_manifest,
    validate_manifest,
)


class LibraryManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load_manifest(Path(__file__).with_name("manifest.json"))

    def test_seed_manifest_is_valid(self):
        self.assertEqual(validate_manifest(self.manifest), [])

    def test_ids_are_unique_and_indexable(self):
        index = build_index(self.manifest)
        self.assertEqual(len(index), sum(len(s["entries"]) for s in self.manifest["shelves"]))
        self.assertIn("G-05", index)

    def test_duplicate_id_is_rejected(self):
        doc = copy.deepcopy(self.manifest)
        duplicate = copy.deepcopy(doc["shelves"][0]["entries"][0])
        doc["shelves"][1]["entries"].append(duplicate)
        self.assertTrue(any("duplicate entry id" in e for e in validate_manifest(doc)))

    def test_dangling_relationship_is_rejected(self):
        doc = copy.deepcopy(self.manifest)
        doc["shelves"][0]["entries"][0]["relations"].append("Z-99")
        self.assertTrue(any("dangling relations reference: Z-99" in e for e in validate_manifest(doc)))

    def test_invalid_evidence_class_is_rejected(self):
        doc = copy.deepcopy(self.manifest)
        doc["shelves"][0]["entries"][0]["evidence"] = "verified-ish"
        self.assertTrue(any("unsupported evidence class" in e for e in validate_manifest(doc)))

    def test_non_monotonic_history_is_rejected(self):
        doc = copy.deepcopy(self.manifest)
        entry = doc["shelves"][0]["entries"][0]
        entry["version"] = 2
        entry["history"].append({"version": 1, "change": "bad", "reason": "duplicate version"})
        self.assertTrue(any("history versions must be strictly increasing" in e for e in validate_manifest(doc)))

    def test_latest_history_must_match_current_version(self):
        doc = copy.deepcopy(self.manifest)
        doc["shelves"][0]["entries"][0]["version"] = 2
        self.assertTrue(any("current version must match latest history version" in e for e in validate_manifest(doc)))

    def test_title_collision_is_reported(self):
        doc = copy.deepcopy(self.manifest)
        doc["shelves"][0]["entries"][1]["title"] = "  ai AS a data HOLDER "
        errors = validate_manifest(doc)
        self.assertTrue(any("possible duplicate titles" in e for e in errors))

    def test_declared_contradictions_are_deduplicated(self):
        doc = copy.deepcopy(self.manifest)
        doc["shelves"][0]["entries"][0]["contradicts"] = ["C-02"]
        doc["shelves"][0]["entries"][1]["contradicts"] = ["C-01"]
        conflicts = find_contradictions(doc)
        self.assertEqual(len(conflicts), 1)
        self.assertEqual((conflicts[0]["left"], conflicts[0]["right"]), ("C-01", "C-02"))

    def test_empty_change_reason_is_rejected(self):
        doc = copy.deepcopy(self.manifest)
        doc["shelves"][0]["entries"][0]["history"][0]["reason"] = " "
        self.assertTrue(any("history records require non-empty change and reason" in e for e in validate_manifest(doc)))

    def test_json_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.json"
            path.write_text(json.dumps(self.manifest), encoding="utf-8")
            loaded = load_manifest(path)
            self.assertEqual(validate_manifest(loaded), [])

    def test_malformed_evidence_classes_do_not_crash_validator(self):
        doc = copy.deepcopy(self.manifest)
        doc["evidence_classes"] = [["not", "hashable"]]
        self.assertTrue(any("evidence_classes must contain exactly" in e for e in validate_manifest(doc)))

    def test_malformed_relationship_container_is_reported_without_crash(self):
        doc = copy.deepcopy(self.manifest)
        doc["shelves"][0]["entries"][0]["relations"] = None
        self.assertTrue(any("relations must be a list" in e for e in validate_manifest(doc)))


if __name__ == "__main__":
    unittest.main()
