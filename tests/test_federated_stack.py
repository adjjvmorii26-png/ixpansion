import unittest

from federated_stack import (
    carbon_aware_weights,
    rank_clusters_by_carbon,
    run_1_3_stack,
    select_primary_federate,
    sphere,
)


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


if __name__ == "__main__":
    unittest.main()