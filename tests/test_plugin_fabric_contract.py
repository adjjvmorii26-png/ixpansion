import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / ".workbench" / "plugin-registry.yaml"

class PluginFabricContractTests(unittest.TestCase):
    def test_core_adapters_are_registered(self):
        text = REGISTRY.read_text(encoding="utf-8")
        for name in ("github:", "notion:", "google_drive:", "supabase:", "vercel:", "composio:", "dropbox:", "figma:", "canva:"):
            with self.subTest(adapter=name):
                self.assertIn(name, text)

    def test_safety_gates_are_explicit(self):
        text = REGISTRY.read_text(encoding="utf-8")
        self.assertIn("destructive_actions_require_approval: true", text)
        self.assertIn("deployment_requires_approval: true", text)
        self.assertIn("merge_requires_approval: true", text)

    def test_skills_declare_capabilities_and_roots(self):
        for path in (
            ROOT / "skills/r1/plugin_adapter_contract/SKILL.md",
            ROOT / "skills/r1/evidence_ledger/SKILL.md",
        ):
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertIn("## Capabilities", text)
                self.assertIn("## Roots", text)
                self.assertIn("### ", text)

if __name__ == "__main__":
    unittest.main()
