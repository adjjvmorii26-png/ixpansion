import tempfile
import unittest
from pathlib import Path

from scripts.validate_skills import validate_skills


class SkillManifestTests(unittest.TestCase):
    def make_repo(self, files):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        for relative, content in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        self.addCleanup(temp.cleanup)
        return root

    def test_valid_frontmatter_passes(self):
        root = self.make_repo({
            "skills/example/SKILL.md":
                "---\nname: example-skill\ndescription: A reusable example capability.\n---\n# Example\n"
        })
        report = validate_skills(root)
        self.assertEqual(report.errors, [])
        self.assertEqual(report.checked, 1)

    def test_legacy_skill_is_accepted_with_warning(self):
        root = self.make_repo({
            "skills/legacy/SKILL.md": "# Legacy skill\n\nExisting format.\n"
        })
        report = validate_skills(root)
        self.assertEqual(report.errors, [])
        self.assertEqual(len(report.warnings), 1)

    def test_missing_description_fails(self):
        root = self.make_repo({
            "skills/example/SKILL.md": "---\nname: example\n---\n# Example\n"
        })
        report = validate_skills(root)
        self.assertTrue(any("description" in item for item in report.errors))

    def test_duplicate_names_fail(self):
        content = "---\nname: shared-name\ndescription: Shared skill description.\n---\n"
        root = self.make_repo({
            "skills/one/SKILL.md": content,
            "skills/two/SKILL.md": content,
        })
        report = validate_skills(root)
        self.assertTrue(any("duplicate skill name" in item for item in report.errors))

    def test_unclosed_frontmatter_fails(self):
        root = self.make_repo({
            "skills/example/SKILL.md": "---\nname: example\ndescription: Example skill description.\n"
        })
        report = validate_skills(root)
        self.assertTrue(any("not closed" in item for item in report.errors))

    def test_missing_skills_directory_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            report = validate_skills(Path(temp))
        self.assertTrue(any("skills directory not found" in item for item in report.errors))


if __name__ == "__main__":
    unittest.main()
