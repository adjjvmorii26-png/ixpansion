import tempfile
import unittest
from pathlib import Path

from scripts.validate_skills import validate_skills


class SkillVitalityTests(unittest.TestCase):
    def repo(self, files):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        for name, content in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        self.addCleanup(temp.cleanup)
        return root

    def test_discovers_skill_files_across_repository_roots(self):
        root = self.repo({
            "skills/a/SKILL.md": "---\nname: alpha\ndescription: A sufficiently long description.\n---\n",
            "codetools/plugins/x/SKILL.md": "---\nname: beta\ndescription: Another sufficiently long description.\n---\n",
        })
        self.assertEqual(validate_skills(root).checked, 2)

    def test_missing_frontmatter_fails(self):
        report = validate_skills(self.repo({"skills/a/SKILL.md": "# no metadata"}))
        self.assertTrue(any("missing YAML frontmatter" in item for item in report.errors))

    def test_duplicate_names_fail(self):
        doc = "---\nname: shared\ndescription: A sufficiently long description.\n---\n"
        report = validate_skills(self.repo({"skills/a/SKILL.md": doc, "skills/b/SKILL.md": doc}))
        self.assertTrue(any("duplicate skill name" in item for item in report.errors))

    def test_unclosed_frontmatter_fails(self):
        doc = "---\nname: alpha\ndescription: A sufficiently long description.\n"
        report = validate_skills(self.repo({"skills/a/SKILL.md": doc}))
        self.assertTrue(any("not closed" in item for item in report.errors))

    def test_secret_literal_fails(self):
        doc = "---\nname: alpha\ndescription: A sufficiently long description.\n---\n"
        report = validate_skills(self.repo({
            "skills/a/SKILL.md": doc + "token=12345678:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijk"
        }))
        self.assertTrue(any("credential literal" in item for item in report.errors))

    def test_direct_production_push_fails(self):
        doc = "---\nname: alpha\ndescription: A sufficiently long description.\n---\n"
        report = validate_skills(self.repo({"skills/a/SKILL.md": doc + "\ngit push origin main\n"}))
        self.assertTrue(any("production/default-branch" in item for item in report.errors))

    def test_high_impact_language_warns_without_boundary(self):
        doc = "---\nname: alpha\ndescription: A sufficiently long description.\n---\nDelete obsolete module."
        report = validate_skills(self.repo({"skills/a/SKILL.md": doc}))
        self.assertEqual(report.errors, [])
        self.assertEqual(len(report.warnings), 1)

    def test_safety_cue_suppresses_high_impact_warning(self):
        doc = "---\nname: alpha\ndescription: A sufficiently long description.\n---\nDelete only after explicit approval and rollback checkpoint."
        report = validate_skills(self.repo({"skills/a/SKILL.md": doc}))
        self.assertEqual(report.warnings, [])

    def test_no_skill_files_fails(self):
        report = validate_skills(self.repo({"README.md": "nothing"}))
        self.assertTrue(any("no SKILL.md" in item for item in report.errors))


if __name__ == "__main__":
    unittest.main()
