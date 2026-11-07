import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class WorkbenchScaffoldTests(unittest.TestCase):
    def test_registry_declares_core_integrations(self):
        text = (ROOT / ".workbench/plugin-registry.yaml").read_text()
        for adapter in ("github:", "notion:", "google_drive:", "supabase:", "vercel:", "composio:"):
            with self.subTest(adapter=adapter):
                self.assertIn(adapter, text)

    def test_safety_gates_are_explicit(self):
        text = (ROOT / ".workbench/plugin-registry.yaml").read_text()
        self.assertIn("destructive_actions_require_approval: true", text)
        self.assertIn("deployment_requires_approval: true", text)
        self.assertIn("merge_requires_approval: true", text)

    def test_orchestrator_has_verification_step(self):
        text = (ROOT / "skills/workbench-orchestrator/SKILL.md").read_text()
        self.assertIn("Verify by reading back", text)
        self.assertIn("evidence", text.lower())

if __name__ == "__main__":
    unittest.main()
