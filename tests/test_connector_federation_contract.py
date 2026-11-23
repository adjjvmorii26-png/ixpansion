import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = [
    ROOT / "skills/capability-contract-compiler/SKILL.md",
    ROOT / "skills/federation-shadow-twin/SKILL.md",
    ROOT / "skills/connector-chaos-simulator/SKILL.md",
]
GEM = ROOT / "gems/connector-federation-lab/GEM.md"
MANIFEST = ROOT / "gems/connector-federation-lab/manifest.json"


class ConnectorFederationContractTests(unittest.TestCase):
    def test_skill_frontmatter_and_unique_names(self):
        names = []
        for path in SKILLS:
            body = path.read_text(encoding="utf-8")
            self.assertTrue(body.startswith("---\n"))
            frontmatter = body.split("---", 2)[1]
            match = re.search(r"^name:\\s*([a-z0-9-]+)$", frontmatter, re.M)
            self.assertIsNotNone(match)
            names.append(match.group(1))
        self.assertEqual(len(names), len(set(names)))

    def test_seed_identity_and_plugin_release(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        gem_text = GEM.read_text(encoding="utf-8")
        self.assertIn(manifest["canonical_seed"]["page_id"], gem_text)
        self.assertEqual(
            manifest["plugin"]["release_id"],
            "pluginrel_6b04d217bea0819180d6a0830a7449a2",
        )
        self.assertEqual(manifest["status"], "CANDIDATE")

    def test_manifest_does_not_invent_source_evidence(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["implementation"]["source_commit"], "UNSET")
        self.assertEqual(manifest["implementation"]["sha256"], "NOT_COMPUTED")
        self.assertIsNone(manifest["promotion"]["approval_ref"])

    def test_synthetic_only_and_live_verification_boundary(self):
        body = "\\n".join(path.read_text(encoding="utf-8") for path in SKILLS)
        self.assertIn("fake transports", body.lower())
        self.assertIn("synthetic", body.lower())
        self.assertIn("live provider compatibility", body.lower())
        self.assertIn("separate approval", body.lower())


if __name__ == "__main__":
    unittest.main()
