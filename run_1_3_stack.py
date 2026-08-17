#!/usr/bin/env python3
"""Run the local, deterministic 1.3 federation demonstration."""

import json

from federated_stack import run_1_3_stack


if __name__ == "__main__":
    output = run_1_3_stack(
        green_scores={"cluster-0": 0.95, "cluster-1": 0.4, "cluster-2": 0.7}
    )
    print(json.dumps({key: value for key, value in output.items() if key != "si"}, indent=2))
    print("si_fit", output["si"]["best_fitness"], "winner", output["si"]["winner_cluster"])