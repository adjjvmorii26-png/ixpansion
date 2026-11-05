import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "labs" / "world-canvas-gem-harness"
MANIFEST = LAB / "skill-manifest.json"
SCENARIOS = LAB / "scenario-registry.json"
EVIDENCE_CONTRACT = LAB / "evidence-contract.json"


class WorldCanvasGemHarnessTests(unittest.TestCase):
    def test_manifest_contract_and_boundaries(self):
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(data["runtime"], "browser-local")
        self.assertIn("Gemini API execution", data["non_capabilities"])
        self.assertEqual(data["version"], "0.3.0")
        self.assertEqual(data["registry"]["system"], "wave733_skill_builder")
        self.assertEqual(data["scenarios"]["path"], "labs/world-canvas-gem-harness/scenario-registry.json")
        self.assertEqual(data["evidence_contract"]["path"], "labs/world-canvas-gem-harness/evidence-contract.json")

    def test_entrypoint_and_skill_files_exist(self):
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertTrue((LAB / data["entrypoint"]).is_file())
        for item in data["skills"]:
            path = ROOT / item["path"]
            self.assertTrue(path.is_file(), item["path"])
            content = path.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("---\\nname: "), item["name"])
            frontmatter = content.split("---", 2)[1]
            self.assertIn("name:", frontmatter)
            self.assertIn("description:", frontmatter)
            self.assertIn("## Capabilities", content)
            self.assertIn("## Roots", content)
            commands = [line[3:line.find("`", 3)] for line in content.splitlines()
                        if line.startswith("- `") and line.find("`", 3) > 3]
            self.assertTrue(commands, item["name"])
            for command in commands:
                self.assertIn(f"### {command}", content, f"{item['name']} missing command example: {command}")

    def test_skill_builder_registry_is_synced(self):
        data = json.loads((ROOT / "data" / "wave733_skill_builder.json").read_text(encoding="utf-8"))
        for name in ("world_canvas_gem_harness", "dual_lens", "zero_copy", "forge_breakers"):
            self.assertIn(name, data["skills_catalog"])
            self.assertIn(name, {item["name"] for item in data["generated"]})

    def test_scenario_registry_is_versioned_and_well_formed(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        registry = json.loads(SCENARIOS.read_text(encoding="utf-8"))
        self.assertEqual(registry["schema"], manifest["scenarios"]["schema"])
        self.assertEqual(registry["execution"], "local-deterministic")
        ids = [item["id"] for item in registry["scenarios"]]
        self.assertEqual(len(ids), len(set(ids)), "scenario IDs must be unique")
        known_skills = {item["name"] for item in manifest["skills"]}
        for scenario in registry["scenarios"]:
            self.assertTrue(scenario["version"])
            self.assertIn(scenario["skill"], known_skills)
            self.assertIsInstance(scenario["seed"], int)
            self.assertTrue(scenario["assertions"])
            self.assertIsInstance(scenario["inputs"], dict)

    def test_evidence_contract_requires_lineage_without_overclaiming(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        contract = json.loads(EVIDENCE_CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(contract["schema"], manifest["evidence_contract"]["schema"])
        for field in ("skill_name", "skill_version", "scenario_id", "scenario_version",
                      "source_commit", "runtime", "execution_mode", "executed_at", "checks"):
            self.assertIn(field, contract["required_fields"])
        self.assertTrue(any("not a signature" in rule for rule in contract["trust_rules"]))
        self.assertTrue(any("never inferred" in rule for rule in contract["trust_rules"]))

    def test_harness_exposes_evidence_and_skill_runners(self):
        html = (LAB / "index.html").read_text(encoding="utf-8")
        for token in ("run-all", "export-report", "dual-lens", "zero-copy", "forge-breakers", "gem-skill-run", "stack.length>100", "65536"):
            self.assertIn(token, html)
        for forbidden in ("fetch(", "XMLHttpRequest", "WebSocket(", "eval(", "new Function("):
            self.assertNotIn(forbidden, html)


if __name__ == "__main__":
    unittest.main()
