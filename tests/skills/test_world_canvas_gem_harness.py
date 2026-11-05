import json
import re
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
        self.assertEqual(data["registry"]["system"], "wave733_skill_builder")

    def test_entrypoint_and_skill_files_exist(self):
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertTrue((LAB / data["entrypoint"]).is_file())
        for item in data["skills"]:
            path = ROOT / item["path"]
            self.assertTrue(path.is_file(), item["path"])
            content = path.read_text(encoding="utf-8")
            self.assertRegex(content, r"(?s)^---\\nname: [^\\n]+\\ndescription: .+?\\n---")
            self.assertIn("## Capabilities", content)
            self.assertIn("## Roots", content)
            commands = re.findall(r"^- \`([^\`]+)\`", content, re.MULTILINE)
            self.assertTrue(commands, item["name"])
            for command in commands:
                self.assertIn(f"### {command}", content, f"{item['name']} missing command example: {command}")

    def test_skill_builder_registry_is_synced(self):
        data = json.loads((ROOT / "data" / "wave733_skill_builder.json").read_text(encoding="utf-8"))
        for name in ("world_canvas_gem_harness", "dual_lens", "zero_copy", "forge_breakers"):
            self.assertIn(name, data["skills_catalog"])
            self.assertIn(name, {item["name"] for item in data["generated"]})

    def test_harness_exposes_evidence_and_skill_runners(self):
        html = (LAB / "index.html").read_text(encoding="utf-8")
        for token in ("run-all", "export-report", "dual-lens", "zero-copy", "forge-breakers", "gem-skill-run"):
            self.assertIn(token, html)
        for forbidden in ("fetch(", "XMLHttpRequest", "WebSocket(", "eval(", "new Function("):
            self.assertNotIn(forbidden, html)

if __name__ == "__main__":
    unittest.main()
