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


if __name__ == "__main__":
    unittest.main()
