#!/usr/bin/env python3
"""
Closed-Loop Evolutionary Physics Kernel Integration
Evolve expressions, benchmark against baseline lattice, write winning kernel.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

from genetic_sandbox import evolve, evaluate_expr
from swarm_wasm_lattice import run_wasm_lattice

KERNEL_OUT = Path("/home/workdir/artifacts/simulations/evolved_kernel.json")
KERNEL_JS_SNIPPET = Path("/home/workdir/artifacts/simulations/evolved_update.expr")


def baseline_energy(n: int = 8, steps: int = 12) -> float:
    r = run_wasm_lattice(n=n, steps=steps, seed=0.4)
    return float(r.get("final_energy") or 0)


def closed_loop(generations: int = 4, population: int = 6) -> dict:
    base = baseline_energy()
    evo = evolve(generations=generations, population=population)
    best_expr = evo.get("best_expr") or "c"
    fit, meta = evaluate_expr(best_expr, n=8, steps=12)
    record = {
        "baseline_energy": base,
        "evolved_fitness": evo.get("best_fitness"),
        "evolved_expr": best_expr,
        "eval_meta": meta,
        "history": evo.get("history"),
        "hot_swap_ready": fit < float("inf"),
    }
    KERNEL_OUT.write_text(json.dumps(record, indent=2, default=str))
    KERNEL_JS_SNIPPET.write_text(best_expr)
    # optional: patch note for ixpansion_lattice.js consumers
    note = Path("/home/workdir/artifacts/simulations/HOT_SWAP.md")
    note.write_text(
        f"# Hot-swap kernel\n\nExpr: `{best_expr}`\n\n"
        f"Replace the core update term in ixpansion_lattice.js with this expression "
        f"(variables: c, neigh, seed, t).\n"
    )
    return record


if __name__ == "__main__":
    r = closed_loop(3, 5)
    print(json.dumps({k: r[k] for k in r if k != "history"}, indent=2, default=str))
  
