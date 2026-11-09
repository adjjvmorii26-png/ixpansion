import json
import tempfile
import unittest
from pathlib import Path

from skill_genome_registry import load_snapshot, main, validate_records

BASE = {"id": "sk_a", "slug": "skill-a", "title": "Skill A", "provider": "Example",
        "source_of_truth": "notion://seed/a", "evidence_state": "VERIFIED",
        "runtime_binding": "unbound", "dependencies": []}


class RegistryValidationTests(unittest.TestCase):
    def codes(self, records):
        return {f["code"] for f in validate_records(records)["findings"]}

    def test_clean_record_has_no_findings(self):
        r = validate_records([BASE.copy()])
        self.assertEqual((r["error_count"], r["warning_count"]), (0, 0))
        self.assertTrue(r["promotion_allowed"])

    def test_duplicate_ids_are_rejected(self):
        self.assertIn("DUPLICATE_ID", self.codes([BASE.copy(), BASE.copy()]))

    def test_duplicate_slugs_are_rejected(self):
        self.assertIn("DUPLICATE_SLUG", self.codes([BASE.copy(), {**BASE, "id": "sk_b"}]))

    def test_orphan_dependency_is_rejected(self):
        self.assertIn("ORPHAN_DEPENDENCY", self.codes([{**BASE, "dependencies": ["sk_missing"]}]))

    def test_missing_evidence_is_not_promotable(self):
        r = validate_records([{**BASE, "evidence_state": "NOT_RUN"}])
        self.assertIn("INCOMPLETE_EVIDENCE", {f["code"] for f in r["findings"]})
        self.assertFalse(r["promotion_allowed"])

    def test_missing_required_fields_are_reported(self):
        self.assertIn("MISSING_FIELD", self.codes([{"id": "sk_x"}]))

    def test_invalid_slug_and_unknown_evidence_are_reported(self):
        self.assertTrue({"INVALID_SLUG", "UNKNOWN_EVIDENCE_STATE"} <=
                        self.codes([{**BASE, "slug": "Not A Slug", "evidence_state": "GREEN"}]))

    def test_runtime_binding_must_be_explicit(self):
        self.assertIn("UNDECLARED_RUNTIME_BINDING", self.codes([{**BASE, "runtime_binding": ""}]))

    def test_input_records_are_not_mutated(self):
        item = BASE.copy()
        before = item.copy()
        validate_records([item])
        self.assertEqual(item, before)

    def test_non_object_record_is_reported(self):
        self.assertIn("INVALID_RECORD", self.codes([None]))

    def test_dependencies_must_be_a_list(self):
        self.assertIn("INVALID_DEPENDENCIES", self.codes([{**BASE, "dependencies": "sk_b"}]))

    def test_snapshot_accepts_wrapped_skills_array(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "snapshot.json"
            path.write_text(json.dumps({"skills": [BASE]}), encoding="utf-8")
            self.assertEqual(load_snapshot(path), [BASE])

    def test_snapshot_rejects_non_array_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "snapshot.json"
            path.write_text('{"items":[]}', encoding="utf-8")
            with self.assertRaises(ValueError):
                load_snapshot(path)

    def test_cli_refuses_to_overwrite_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "snapshot.json"
            original = json.dumps([BASE])
            path.write_text(original, encoding="utf-8")
            self.assertEqual(main([str(path), "--output", str(path)]), 2)
            self.assertEqual(path.read_text(encoding="utf-8"), original)

    def test_cli_writes_report_to_separate_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "snapshot.json"
            output = Path(tmp) / "report.json"
            source.write_text(json.dumps([BASE]), encoding="utf-8")
            self.assertEqual(main([str(source), "--output", str(output)]), 0)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["record_count"], 1)


if __name__ == "__main__":
    unittest.main()
