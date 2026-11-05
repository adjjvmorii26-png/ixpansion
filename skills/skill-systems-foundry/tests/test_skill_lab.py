import json
import tempfile
import unittest
from pathlib import Path
from skill_lab import compatibility, dependency_graph, digest, drift, fuzz_cases, scan

class FoundryTests(unittest.TestCase):
    def test_scan_finds_missing_description(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "sample"
            folder.mkdir()
            (folder / "SKILL.md").write_text("---\nname: sample\n---\n")
            self.assertIn("DESCRIPTION_MISSING",
                          [x["code"] for x in scan(Path(tmp))])

    def test_graph_finds_missing_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "sample"
            folder.mkdir()
            (folder / "SKILL.md").write_text(
                "---\nname: sample\ndescription: test\ndepends_on: absent\n---\n")
            self.assertEqual(dependency_graph(Path(tmp))["edges"][0]["status"],
                             "MISSING_TARGET")

    def test_fuzz_is_repeatable_and_bounded(self):
        self.assertEqual(fuzz_cases(1337, 12), fuzz_cases(1337, 12))
        self.assertEqual(len(fuzz_cases(1, 900)), 256)

    def test_compatibility_warns_on_platform_leak(self):
        result = compatibility("name: test mcp__adapter", "portable")
        self.assertEqual(result["status"], "WARN")

    def test_drift_detects_export_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "seed_snapshot.md").write_text("seed")
            (folder / "SKILL.md").write_text("changed")
            (folder / "provenance.json").write_text(json.dumps({
                "source_sha256": digest("seed"),
                "export_sha256": digest("old")
            }))
            self.assertIn("EXPORT_DRIFT",
                          [x["code"] for x in drift(folder)])

if __name__ == "__main__":
    unittest.main()
