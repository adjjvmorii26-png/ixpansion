import copy
import json
import tempfile
import unittest
from pathlib import Path

from proof_contract import canon_promotion_errors, validate_proof_contract
from library_validator import (
    build_index, find_contradictions, load_manifest,
    validate_lineage_delta, validate_manifest,
)


class LibraryCoreIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load_manifest(Path(__file__).with_name("manifest.json"))

    def test_golden_manifest_is_valid(self):
        self.assertEqual(validate_manifest(self.manifest), [])

    def test_ids_are_unique_and_indexable(self):
        index = build_index(self.manifest)
        self.assertEqual(len(index), sum(len(s["entries"]) for s in self.manifest["shelves"]))
        self.assertIn("G-03", index)

    def test_duplicate_id_is_rejected(self):
        doc = copy.deepcopy(self.manifest)
        duplicate = copy.deepcopy(doc["shelves"][0]["entries"][0])
        doc["shelves"][1]["entries"].append(duplicate)
        self.assertTrue(any("duplicate entry id" in e for e in validate_manifest(doc)))

    def test_dangling_relationship_is_rejected(self):
        doc = copy.deepcopy(self.manifest)
        doc["shelves"][0]["entries"][0]["relations"].append("Z-99")
        self.assertTrue(any("dangling relations reference: Z-99" in e for e in validate_manifest(doc)))

    def test_retired_ids_cannot_be_reused(self):
        doc = copy.deepcopy(self.manifest)
        eid = doc["shelves"][0]["entries"][0]["id"]
        doc["identity_registry"][0]["status"] = "retired"
        self.assertTrue(any(f"{eid} is active but its reserved ID status is retired" in e for e in validate_manifest(doc)))

    def test_missing_registry_record_is_rejected(self):
        doc = copy.deepcopy(self.manifest)
        doc["identity_registry"] = doc["identity_registry"][1:]
        self.assertTrue(any("missing from permanent identity_registry" in e for e in validate_manifest(doc)))

    def test_invalid_evidence_class_is_rejected(self):
        doc = copy.deepcopy(self.manifest)
        doc["shelves"][0]["entries"][0]["evidence"] = "verified-ish"
        self.assertTrue(any("unsupported evidence class" in e for e in validate_manifest(doc)))

    def test_evidence_transition_requires_event(self):
        doc = copy.deepcopy(self.manifest)
        entry = doc["shelves"][0]["entries"][0]
        entry["evidence"] = "hypothesis"
        self.assertTrue(any("current evidence must match latest history tostate" in e for e in validate_manifest(doc)))

    def test_jump_more_than_one_level_is_rejected(self):
        base = copy.deepcopy(self.manifest)
        head = copy.deepcopy(self.manifest)
        entry = head["shelves"][0]["entries"][0]
        entry["evidence"] = "verified"
        entry["history"][-1]["tostate"] = "verified"
        self.assertTrue(any("jumps more than one evidence level" in e for e in validate_lineage_delta(base, head)))

    def test_history_requires_provenance_fields(self):
        doc = copy.deepcopy(self.manifest)
        doc["shelves"][0]["entries"][0]["history"][0]["evidence_ref"] = ""
        self.assertTrue(any("requires non-empty evidence_ref" in e for e in validate_manifest(doc)))

    def test_downgrade_requires_reason_and_trigger(self):
        doc = copy.deepcopy(self.manifest)
        entry = doc["shelves"][0]["entries"][0]
        entry["history"].append({
            "version":2,"change":"Downgrade","reason":"","fromstate":"idea","tostate":"idea",
            "timestamp":"2026-10-15T00:00:00Z","actor":"agent","evidence_ref":"issue"
        })
        entry["version"] = 2
        self.assertTrue(any("history[1] must change evidence state" in e or "downgrade requires reason and recognized trigger" in e for e in validate_manifest(doc)))

    def test_declared_contradictions_are_deduplicated(self):
        doc = copy.deepcopy(self.manifest)
        a = doc["shelves"][0]["entries"][0]
        b = doc["shelves"][0]["entries"][1]
        a["contradicts"] = [b["id"]]
        b["contradicts"] = [a["id"]]
        doc["contradiction_atlas"] = [{
            "id":"F-001","tag":"frontier","entries":[a["id"],b["id"]],
            "dimension":"correctness","description":"Example conflict for regression test",
            "shelf":"Core Concepts","status":"active","resolution_path":"needs experiment",
            "follow_up":"Add a falsifiable experiment to settle the claim."
        }]
        self.assertEqual(len(find_contradictions(doc)), 1)
        self.assertEqual(validate_manifest(doc), [])

    def test_contradiction_without_atlas_record_is_rejected(self):
        doc = copy.deepcopy(self.manifest)
        a = doc["shelves"][0]["entries"][0]
        a["contradicts"] = [doc["shelves"][0]["entries"][1]["id"]]
        self.assertTrue(any("missing from contradiction_atlas" in e for e in validate_manifest(doc)))

    def test_atlas_requires_bilateral_entry_tags(self):
        doc = copy.deepcopy(self.manifest)
        a = doc["shelves"][0]["entries"][0]
        b = doc["shelves"][0]["entries"][1]
        a["contradicts"] = [b["id"]]
        b["contradicts"] = [a["id"]]
        doc["contradiction_atlas"] = [{
            "id":"F-001","tag":"oops","entries":[a["id"],b["id"]],
            "dimension":"correctness","description":"Conflict",
            "shelf":"Core Concepts","status":"active","resolution_path":"needs experiment",
            "follow_up":"Write experiment."
        }]
        self.assertTrue(any("must be tagged frontier" in e for e in validate_manifest(doc)))

    def test_title_collision_is_reported(self):
        doc = copy.deepcopy(self.manifest)
        doc["shelves"][0]["entries"][1]["title"] = "  ai AS a data HOLDER "
        self.assertTrue(any("possible duplicate titles" in e for e in validate_manifest(doc)))

    def test_json_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.json"
            path.write_text(json.dumps(self.manifest), encoding="utf-8")
            self.assertEqual(validate_manifest(load_manifest(path)), [])

    def test_malformed_evidence_classes_do_not_crash_validator(self):
        doc = copy.deepcopy(self.manifest)
        doc["evidence_classes"] = [["not", "hashable"]]
        self.assertTrue(any("evidence_classes must exactly" in e for e in validate_manifest(doc)))

    def test_retired_id_cannot_be_reactivated_in_pr_delta(self):
        base = copy.deepcopy(self.manifest)
        head = copy.deepcopy(self.manifest)
        eid = base["identity_registry"][0]["id"]
        base["identity_registry"][0]["status"] = "retired"
        head["identity_registry"][0]["status"] = "active"
        self.assertTrue(any("cannot be reactivated" in e for e in validate_lineage_delta(base, head)))

    def test_reserved_id_cannot_disappear_in_pr_delta(self):
        base = copy.deepcopy(self.manifest)
        head = copy.deepcopy(self.manifest)
        eid = head["identity_registry"][0]["id"]
        head["identity_registry"] = [r for r in head["identity_registry"] if r["id"] != eid]
        self.assertTrue(any(f"reserved ID {eid} was removed" in e for e in validate_lineage_delta(base, head)))

    def _proof(self, entry_id="G-03", kind="ci_run"):
        proof = {
            "id": "P-0001",
            "kind": kind,
            "subject": {"entry_id": entry_id, "claim": "The declared regression suite passes for this exact revision."},
            "artifact": {"uri": "https://example.invalid/artifacts/library-test-report.json", "sha256": "a" * 64},
            "verifier": {"name": "GitHub Actions", "version": "v1"},
            "procedure": {"command": ["python", "-m", "unittest", "-v"], "environment": "python:3.11", "reproducible": True},
            "result": {"status": "passed", "observed_at": "2026-10-15T00:00:00Z"},
        }
        if kind == "ci_run":
            proof["run"] = {
                "run_id": 123456,
                "run_url": "https://github.com/example/repo/actions/runs/123456",
                "workflow": "Library Core integrity gate",
                "commit_sha": "b" * 40,
                "conclusion": "success",
            }
        return proof

    def test_empty_proof_registry_is_valid_until_an_entry_claims_canon(self):
        self.assertEqual(validate_proof_contract(self.manifest), [])

    def test_verified_entry_without_proof_refs_is_rejected(self):
        doc = copy.deepcopy(self.manifest)
        entry = next(e for s in doc["shelves"] for e in s["entries"] if e["id"] == "G-03")
        entry["evidence"] = "verified"
        entry["lifecycle"]["label"] = "Canon"
        entry["lifecycle"].update({"version_pin": "commit:" + "b" * 40, "known_limitations": [], "contradiction_watchlist": []})
        self.assertTrue(any("cannot be Canon without lifecycle.proof_refs" in e for e in validate_proof_contract(doc)))

    def test_canon_requires_a_linked_successful_machine_proof(self):
        doc = copy.deepcopy(self.manifest)
        entry = next(e for s in doc["shelves"] for e in s["entries"] if e["id"] == "G-03")
        entry["evidence"] = "tested"
        entry["lifecycle"].update({"label": "Trialed", "version_pin": "commit:" + "b" * 40, "known_limitations": [], "contradiction_watchlist": [], "proof_refs": ["P-0001"]})
        doc["proof_objects"] = [self._proof()]
        self.assertEqual(canon_promotion_errors(doc, "G-03"), [])

    def test_canon_gate_rejects_failed_ci_proof(self):
        doc = copy.deepcopy(self.manifest)
        entry = next(e for s in doc["shelves"] for e in s["entries"] if e["id"] == "G-03")
        entry["evidence"] = "tested"
        entry["lifecycle"].update({"label": "Trialed", "version_pin": "commit:" + "b" * 40, "known_limitations": [], "contradiction_watchlist": [], "proof_refs": ["P-0001"]})
        proof = self._proof()
        proof["run"]["conclusion"] = "failure"
        doc["proof_objects"] = [proof]
        self.assertTrue(canon_promotion_errors(doc, "G-03"))

    def test_proof_object_with_malformed_digest_is_rejected(self):
        doc = copy.deepcopy(self.manifest)
        proof = self._proof()
        proof["artifact"]["sha256"] = "not-a-digest"
        doc["proof_objects"] = [proof]
        self.assertTrue(any("SHA-256 digest" in e for e in validate_proof_contract(doc)))

    def test_file_digest_is_checked_against_bytes(self):
        from proof_contract import validate_proof_contract
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact = root / "report.txt"
            artifact.write_text("actual proof bytes", encoding="utf-8")
            import hashlib
            proof = {
                "id":"P-0002","kind":"file_digest",
                "subject":{"entry_id":"G-03","claim":"Artifact bytes match declared digest."},
                "artifact":{"uri":"repo://report.txt","sha256":"0" * 64},
                "verifier":{"name":"SHA-256","version":"1"},
                "procedure":{"command":["sha256sum","report.txt"],"environment":"python:3.11","reproducible":True},
                "result":{"status":"passed","observed_at":"2026-10-15T00:00:00Z"}
            }
            doc = copy.deepcopy(self.manifest)
            doc["proof_objects"] = [proof]
            errors = validate_proof_contract(doc, root)
            self.assertTrue(any("SHA-256 mismatch" in e for e in errors))
            proof["artifact"]["sha256"] = hashlib.sha256(artifact.read_bytes()).hexdigest()
            self.assertFalse(any("SHA-256 mismatch" in e for e in validate_proof_contract(doc, root)))


if __name__ == "__main__":
    unittest.main()
