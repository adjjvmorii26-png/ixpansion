from pathlib import Path
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/gem-artifact-provenance-compatibility/SKILL.md"
GEM = ROOT / "gems/gem-artifact-provenance-compatibility/GEM.md"
MANIFEST = ROOT / "gems/gem-artifact-provenance-compatibility/manifest.json"


class GemArtifactProvenanceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.gem = GEM.read_text(encoding="utf-8")
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_skill_has_valid_frontmatter_and_unique_name_shape(self):
        self.assertTrue(self.skill.startswith("---\n"))
        header = self.skill.split("---", 2)[1]
        name = re.search(r"^name:\s*([a-z0-9-]+)$", header, re.M)
        description = re.search(r"^description:\s*(.{12,})$", header, re.M)
        self.assertIsNotNone(name)
        self.assertEqual(name.group(1), "gem-artifact-provenance-compatibility")
        self.assertIsNotNone(description)

    def test_skill_and_gem_share_canonical_seed_identity(self):
        page_id = self.manifest["canonical_seed"]["page_id"]
        self.assertIn(page_id, self.gem)
        self.assertEqual(self.manifest["artifact_id"], "gem-artifact-provenance-compatibility")

    def test_manifest_does_not_claim_unobserved_runtime_or_digest(self):
        self.assertEqual(self.manifest["implementation"]["source_commit"], "UNSET")
        self.assertEqual(self.manifest["implementation"]["sha256"], "NOT_COMPUTED")
        self.assertEqual(self.manifest["compatibility"]["gemini_account_activation"], "NOT_TESTED")
        self.assertEqual(self.manifest["promotion"]["state"], "CANDIDATE")

    def test_skill_preserves_explicit_promotion_and_truth_boundaries(self):
        for phrase in (
            "requires a separate explicit authorization",
            "A local parse or archive inspection is not a runtime test",
            "never invent a digest",
            "MISMATCHED",
            "UNVERIFIED",
        ):
            self.assertIn(phrase, self.skill)


if __name__ == "__main__":
    unittest.main()
