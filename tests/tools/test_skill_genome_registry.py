import unittest
from skill_genome_registry import validate_records

BASE = {"id":"sk_a", "slug":"skill-a", "title":"Skill A", "provider":"Example",
        "source_of_truth":"notion://seed/a", "evidence_state":"VERIFIED",
        "runtime_binding":"unbound", "dependencies":[]}

class RegistryValidationTests(unittest.TestCase):
    def test_clean_record_has_no_findings(self):
        r=validate_records([BASE.copy()]); self.assertEqual((r["error_count"],r["warning_count"]),(0,0)); self.assertTrue(r["promotion_allowed"])
    def test_duplicate_ids_are_rejected(self):
        self.assertIn("DUPLICATE_ID",{f["code"] for f in validate_records([BASE.copy(),BASE.copy()])["findings"]})
    def test_duplicate_slugs_are_rejected(self):
        other={**BASE,"id":"sk_b","title":"Skill B"}
        self.assertIn("DUPLICATE_SLUG",{f["code"] for f in validate_records([BASE.copy(),other])["findings"]})
    def test_orphan_dependency_is_rejected(self):
        self.assertIn("ORPHAN_DEPENDENCY",{f["code"] for f in validate_records([{**BASE,"dependencies":["sk_missing"]}])["findings"]})
    def test_missing_evidence_is_not_promotable(self):
        r=validate_records([{**BASE,"evidence_state":"NOT_RUN"}])
        self.assertIn("INCOMPLETE_EVIDENCE",{f["code"] for f in r["findings"]}); self.assertFalse(r["promotion_allowed"])
    def test_missing_required_fields_are_reported(self):
        self.assertGreater(validate_records([{"id":"sk_x"}])["error_count"],0)
    def test_invalid_slug_and_unknown_evidence_are_reported(self):
        codes={f["code"] for f in validate_records([{**BASE,"slug":"Not A Slug","evidence_state":"GREEN"}])["findings"]}
        self.assertTrue({"INVALID_SLUG","UNKNOWN_EVIDENCE_STATE"} <= codes)
    def test_runtime_binding_must_be_explicit(self):
        self.assertIn("UNDECLARED_RUNTIME_BINDING",{f["code"] for f in validate_records([{**BASE,"runtime_binding":""}])["findings"]})
    def test_input_records_are_not_mutated(self):
        item=BASE.copy(); before=item.copy(); validate_records([item]); self.assertEqual(item,before)

if __name__ == "__main__": unittest.main()
