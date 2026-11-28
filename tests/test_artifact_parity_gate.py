import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/artifact-parity-gate/SKILL.md"
GEM = ROOT / "gems/artifact-parity-gate/GEM.md"
MANIFEST = ROOT / "gems/artifact-parity-gate/manifest.json"


class ArtifactParityGateTests(unittest.TestCase):
    def test_skill_frontmatter(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        frontmatter = text.split("---", 2)[1]
        self.assertRegex(frontmatter, r"(?m)^name: artifact-parity-gate$")

    def test_manifest_links_canonical_seed_and_plugin_release(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        gem = GEM.read_text(encoding="utf-8")
        self.assertIn(manifest["canonical_seed"]["page_id"], gem)
        self.assertIn(manifest["plugin"]["release_id"], gem)
        self.assertEqual(manifest["plugin"]["version"], "0.3.0")
        self.assertEqual(manifest["status"], "CANDIDATE")

    def test_no_invented_source_hash_or_approval(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["implementation"]["source_commit"], "UNSET")
        self.assertEqual(manifest["implementation"]["sha256"], "NOT_COMPUTED")
        self.assertIsNone(manifest["promotion"]["approval_ref"])

    def test_evidence_levels_and_quarantine_boundary(self):
        text = SKILL.read_text(encoding="utf-8")
        for token in ("BYTE", "NORMALIZED_TEXT", "METADATA_ONLY", "DRIFTED", "UNVERIFIABLE"):
            self.assertIn(token, text)
        self.assertIn("Never overwrite", text)
        self.assertIn("read it back", text.lower())

    def test_archive_and_extracted_manifest_are_distinct(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("Archives: hash archive bytes separately", text)


if __name__ == "__main__":
    unittest.main()
