import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "labs" / "world-canvas-gem-harness"
MANIFEST = LAB / "skill-manifest.json"

class WorldCanvasGemHarnessTests(unittest.TestCase):
    def test_manifest_contract_and_boundaries(self):
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(data["runtime"], "browser-local")
        self.assertIn("Gemini API execution", data["non_capabilities"])
        self.assertEqual(data["version"], "0.2.0")

    def test_entrypoint_and_skill_files_exist(self):
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertTrue((LAB / data["entrypoint"]).is_file())
        for item in data["skills"]:
            self.assertTrue((ROOT / item["path"]).is_file(), item["path"])

    def test_harness_exposes_evidence_and_skill_runners(self):
        html = (LAB / "index.html").read_text(encoding="utf-8")
        for token in ("run-all", "export-report", "dual-lens", "zero-copy", "forge-breakers", "gem-skill-run"):
            self.assertIn(token, html)

if __name__ == "__main__":
    unittest.main()
