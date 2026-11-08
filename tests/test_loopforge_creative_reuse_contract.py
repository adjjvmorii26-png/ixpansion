"""Contract checks for the LOOPFORGE Creative Reuse skill."""

from pathlib import Path
import re
import unittest


SKILL = Path(__file__).resolve().parents[1] / "skills" / "loopforge-creative-reuse" / "SKILL.md"


class LoopforgeCreativeReuseContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SKILL.read_text(encoding="utf-8")

    def test_skill_has_frontmatter_and_version(self):
        self.assertTrue(self.text.startswith("---\n"))
        self.assertRegex(self.text, r"(?m)^name: loopforge-creative-reuse$")
        self.assertRegex(self.text, r"(?m)^version: 1\.0\.0$")

    def test_stale_lifecycle_has_all_six_states(self):
        for state in ("ACTIVE", "REFRESH", "FORK", "QUARANTINE", "ARCHIVE-CANDIDATE", "NEW-GAP"):
            with self.subTest(state=state):
                self.assertIn(state, self.text)

    def test_library_shelves_cover_requested_reusable_types(self):
        for shelf in ("GEMS", "SEEDS", "SKILLS", "PLUGINS", "BUILDERS", "ARTIFACTS", "KERNELS"):
            with self.subTest(shelf=shelf):
                self.assertIn(shelf, self.text)

    def test_creative_pipelines_are_documented(self):
        for pipeline in ("GIF Foundry", "Meme Engine", "Remix Laboratory", "AI Gallery"):
            with self.subTest(pipeline=pipeline):
                self.assertIn(pipeline, self.text)

    def test_safety_and_evidence_gates_are_present(self):
        for phrase in (
            "preserve original assets",
            "untrusted input",
            "Ask for approval",
            "Do not call a test",
            "A proposed change is not a merged change",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.text)

    def test_test_protocol_includes_focused_and_full_runs(self):
        self.assertIn("Changed-surface tests", self.text)
        self.assertIn("Full suite", self.text)
        self.assertRegex(self.text, r"default 10 iterations")
        self.assertRegex(self.text, r"100 only when runtime is reasonable")


if __name__ == "__main__":
    unittest.main()
