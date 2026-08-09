import unittest

from aether_lattice import AetherLattice
from agent import Agent
from lattice_stack import Machine, MachineLattice
from security_controls import AuditStore, TrustStore


class AetherLatticeTests(unittest.TestCase):
    def make_foundation(self):
        return AetherLattice(
            agent=Agent(name="test-aether"),
            lattice=MachineLattice([
                Machine("healthy", health=0.95, capacity=0.8),
                Machine("reuse", health=0.55, capacity=0.35),
            ]),
            trust=TrustStore(),
            audits=AuditStore(":memory:"),
        )

    def test_snapshot_connects_all_foundation_layers(self):
        foundation = self.make_foundation()
        snapshot = foundation.snapshot()
        self.assertEqual(snapshot["name"], "aether-lattice")
        self.assertEqual(snapshot["agent"]["name"], "test-aether")
        self.assertEqual(snapshot["lattice"]["machines"], 2)
        self.assertIn("winner_cluster", snapshot["federation"])
        self.assertIn("audit_records", snapshot["safety"])
        foundation.audits.close()

    def test_dispatch_allocates_runs_agent_and_audits(self):
        foundation = self.make_foundation()
        result = foundation.dispatch("Inspect the lattice", task_id="task-1")
        self.assertEqual(result["machine_id"], "reuse")
        self.assertEqual(result["agent"]["goal"], "Inspect the lattice")
        self.assertEqual(result["node_trust"], 0.6)
        self.assertEqual(foundation.audits.decisions("task-1")[0][-1], "ALLOCATED")
        foundation.audits.close()

    def test_six_offline_workflows_use_existing_agent_skills(self):
        foundation = self.make_foundation()
        self.assertEqual(len(foundation.workflows()), 6)
        names = {item["name"] for item in foundation.workflows()}
        self.assertEqual(
            names,
            {
                "summarize",
                "extract_tasks",
                "make_checklist",
                "score_priority",
                "normalize_text",
                "dispatch_work",
            },
        )
        self.assertTrue(
            foundation.run_workflow("summarize", "Check this first.")["result"].startswith("Summary:")
        )
        foundation.audits.close()

    def test_workflow_results_are_reusable_by_key(self):
        foundation = self.make_foundation()
        result = foundation.run_workflow("normalize_text", "  reuse   this  ", task_id="saved-1")
        self.assertEqual(result["data_key"], "saved-1")
        self.assertEqual(foundation.load_data("saved-1")["result"], "Normalized: reuse this")
        self.assertEqual(foundation.list_data(), ["saved-1"])
        foundation.audits.close()

    def test_reusable_data_keys_are_normalized_and_values_are_copied(self):
        foundation = self.make_foundation()
        value = {"items": ["one"]}
        saved = foundation.save_data("  note-1  ", value)
        value["items"].append("caller-change")

        self.assertEqual(saved, {"key": "note-1", "value": {"items": ["one"]}})
        self.assertEqual(foundation.load_data("note-1"), {"items": ["one"]})
        foundation.audits.close()

    def test_reusable_data_rejects_unsafe_keys(self):
        foundation = self.make_foundation()
        for key in ("", "has space", "../outside", "x" * 129):
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "data key"):
                foundation.save_data(key, "value")
        foundation.audits.close()

    def test_recycle_data_compiles_redacted_reusable_context(self):
        foundation = self.make_foundation()
        result = foundation.recycle_data(
            "API_KEY=secret-value\nKeep this fact.\nKeep this fact.",
            chunk_size=64,
            task_id="compiled-1",
        )

        self.assertEqual(result["data_key"], "compiled-1")
        self.assertTrue(result["redacted"])
        self.assertNotIn("secret-value", str(result))
        self.assertGreaterEqual(result["approximate_tokens"], 1)
        artifact = {key: value for key, value in result.items() if key != "data_key"}
        self.assertEqual(foundation.load_data("compiled-1"), artifact)
        self.assertTrue(all(len(chunk) <= 64 for chunk in result["chunks"]))
        foundation.audits.close()

    def test_recycle_data_rejects_invalid_chunk_size(self):
        foundation = self.make_foundation()
        with self.assertRaisesRegex(ValueError, "chunk_size"):
            foundation.recycle_data("enough source text", chunk_size=10)
        foundation.audits.close()


if __name__ == "__main__":
    unittest.main()
