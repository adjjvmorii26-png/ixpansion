import unittest

from federated_stack import (
    carbon_aware_weights,
    rank_clusters_by_carbon,
    run_1_3_stack,
    select_primary_federate,
    sphere,
)
from lattice_stack import Machine, MachineLattice, MachineState, build_lattice_stack
from lattice_stack import LatticePolicy


class FederatedStackTests(unittest.TestCase):
    def test_stack_is_deterministic_and_reports_all_layers(self):
        first = run_1_3_stack(green_scores={"cluster-0": 0.95, "cluster-1": 0.4, "cluster-2": 0.7})
        second = run_1_3_stack(green_scores={"cluster-0": 0.95, "cluster-1": 0.4, "cluster-2": 0.7})
        self.assertEqual(first, second)
        self.assertEqual(first["primary_carbon_federate"], "cluster-0")
        self.assertEqual(first["carbon_rank"][0], ("cluster-0", 0.95))
        self.assertEqual(first["scratchpad"]["frames"], 1)
        self.assertEqual(first["si"]["best_fitness"], sphere(first["si"]["best_x"]))

    def test_carbon_helpers_rank_filter_and_normalize(self):
        clusters = ["cluster-0", "cluster-1", "cluster-2"]
        scores = {"cluster-0": 0.9, "cluster-1": 0.4, "cluster-2": 0.7}
        self.assertEqual(
            rank_clusters_by_carbon(clusters, scores),
            [("cluster-0", 0.9), ("cluster-2", 0.7), ("cluster-1", 0.4)],
        )
        self.assertEqual(select_primary_federate(clusters, scores, min_score=0.8), "cluster-0")
        weights = carbon_aware_weights(scores)
        self.assertEqual(weights["cluster-1"], 0.2)
        self.assertEqual(weights["cluster-0"], 1.0)

    def test_empty_cluster_list_is_rejected_by_default_shape(self):
        with self.assertRaises(ValueError):
            run_1_3_stack(n_clusters=0)

    def test_federation_reports_safe_degraded_machine_reuse(self):
        result = run_1_3_stack(green_scores={"cluster-0": 0.9})
        lattice = result["lattice"]
        self.assertEqual(lattice["summary"]["states"]["reusable"], 1)
        self.assertEqual(lattice["noncritical_machine"], "reuse-lane-0")

    def test_lattice_quarantines_untrusted_machines(self):
        lattice = MachineLattice([
            Machine("degraded", health=0.5, capacity=0.8),
            Machine("untrusted", health=0.9, capacity=0.8, trust=0.2),
        ])
        self.assertEqual(lattice.classify(lattice.machines["degraded"]), MachineState.REUSABLE)
        self.assertEqual(lattice.classify(lattice.machines["untrusted"]), MachineState.QUARANTINED)
        self.assertEqual(lattice.allocate("batch", critical=False), "degraded")
        with self.assertRaises(LookupError):
            MachineLattice([Machine("degraded", health=0.5, capacity=0.8)]).allocate(
                "production", critical=True
            )

    def test_lattice_rejects_invalid_machine_values(self):
        with self.assertRaisesRegex(ValueError, "health"):
            MachineLattice([Machine("bad", health=1.1, capacity=0.5)])

        with self.assertRaisesRegex(ValueError, "already registered"):
            MachineLattice([
                Machine("duplicate", health=0.5, capacity=0.5),
                Machine("duplicate", health=0.6, capacity=0.5),
            ])

        with self.assertRaisesRegex(ValueError, "task is required"):
            MachineLattice([Machine("usable", health=0.9, capacity=0.5)]).allocate(" ")

    def test_lattice_builder_returns_reuse_summary(self):
        result = build_lattice_stack([Machine("reuse", health=0.5, capacity=0.4)])
        self.assertEqual(result["noncritical_machine"], "reuse")

        result = build_lattice_stack([Machine("unsafe", health=0.1, capacity=0.4)])
        self.assertIsNone(result["noncritical_machine"])
        self.assertEqual(result["summary"]["quarantined"], ["unsafe"])

    def test_lattice_heartbeat_updates_telemetry_and_expires_stale_nodes(self):
        lattice = MachineLattice(
            [Machine("worker", health=0.9, capacity=0.8)],
            policy=LatticePolicy(heartbeat_timeout=10),
        )
        self.assertEqual(
            lattice.heartbeat("worker", load=0.7, now=100), MachineState.HEALTHY
        )
        self.assertEqual(lattice.machines["worker"].load, 0.7)
        self.assertEqual(
            lattice.classify(lattice.machines["worker"], now=111),
            MachineState.QUARANTINED,
        )

    def test_lattice_heartbeat_rejects_unknown_or_invalid_nodes(self):
        lattice = MachineLattice([Machine("worker", health=0.9, capacity=0.8)])
        with self.assertRaises(KeyError):
            lattice.heartbeat("missing", now=1)
        with self.assertRaisesRegex(ValueError, "load"):
            lattice.heartbeat("worker", load=1.1, now=1)

    def test_lattice_leases_expire_and_release(self):
        lattice = MachineLattice([Machine("worker", health=0.9, capacity=0.8)])
        lease = lattice.acquire("batch", duration=10, now=100)
        self.assertEqual(lease.machine_id, "worker")
        with self.assertRaises(LookupError):
            lattice.allocate("second batch", now=105)
        self.assertEqual(lattice.release("worker"), True)
        self.assertEqual(lattice.allocate("second batch"), "worker")


if __name__ == "__main__":
    unittest.main()