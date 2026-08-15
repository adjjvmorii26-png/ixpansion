#!/usr/bin/env python3
from __future__ import annotations
import json, random, time, math
from typing import Tuple
from ast_sandbox import validate_source

TERMS = ["c", "neigh", "0.5", "0.98", "0.02", "seed"]
OPS = ["+", "-", "*"]

def random_expr(depth: int = 2) -> str:
    if depth <= 0 or random.random() < 0.4:
        return random.choice(TERMS)
    return f"({random_expr(depth-1)} {random.choice(OPS)} {random_expr(depth-1)})"

def make_kernel_source(expr: str) -> str:
    # no imports; sin provided by executor env as sin()
    return f"""def run(n=8, steps=10, seed=0.5, sin=None):
    size = n * n
    a = [sin((i + seed * 100) * 0.17) * 0.5 for i in range(size)]
    b = a[:]
    history = []
    for t in range(steps):
        energy = 0.0
        for x in range(n):
            for y in range(n):
                i = x * n + y
                c = a[i]
                neigh = (a[((x+1)%n)*n+y] + a[((x-1)%n)*n+y] + a[x*n+((y+1)%n)] + a[x*n+((y-1)%n)]) / 4.0
                val = {expr}
                b[i] = val
                energy += val * val
        a, b = b, a
        history.append(energy)
    return {{"final_energy": history[-1] if history else 0.0, "history": history[:], "expr": "{expr}" }}
"""

def mutate(expr: str) -> str:
    return random_expr(2) if random.random() < 0.5 else f"({expr} {random.choice(OPS)} {random.choice(TERMS)})"

def evaluate_expr(expr: str, n: int = 6, steps: int = 8) -> Tuple[float, dict]:
    src = make_kernel_source(expr)
    ok, issues = validate_source(src)
    if not ok:
        return float("inf"), {"error": issues}
    try:
        loc = {}
        exec(compile(src, "<gene>", "exec"), {"__builtins__": {"range": range, "int": int, "float": float}}, loc)
        t0 = time.perf_counter()
        result = loc["run"](n=n, steps=steps, seed=0.4, sin=math.sin)
        dt = time.perf_counter() - t0
        energy = abs(float(result.get("final_energy", 1e9)))
        hist = result.get("history") or []
        # Variance / activity penalty — collapse to near-zero is not a win
        if len(hist) >= 2:
            mean = sum(hist) / len(hist)
            var = sum((x - mean) ** 2 for x in hist) / len(hist)
            std = var ** 0.5
        else:
            std = 0.0
        activity = abs(energy)
        collapse_penalty = 0.0
        if std < 0.01:
            collapse_penalty += 50.0  # hard reject trivial null dynamics
        if activity < 1e-6:
            collapse_penalty += 50.0
        # Prefer moderate energy with temporal structure
        fitness = collapse_penalty + (0.1 / (std + 1e-6)) + dt * 5 + abs(energy - 1.0) * 0.01
        return fitness, {"result": result, "dt": dt, "std": std, "collapse_penalty": collapse_penalty}
    except Exception as e:
        return float("inf"), {"error": str(e)}

def evolve(generations: int = 4, population: int = 6) -> dict:
    pop = [random_expr(2) for _ in range(population)]
    history = []
    best = (float("inf"), "", {})
    for g in range(generations):
        scored = []
        for e in pop:
            fit, meta = evaluate_expr(e)
            scored.append((fit, e, meta))
            if fit < best[0]:
                best = (fit, e, meta)
        scored.sort(key=lambda x: x[0])
        history.append({"gen": g, "best_fitness": scored[0][0], "best_expr": scored[0][1]})
        survivors = [e for fit, e, _ in scored[:max(2, population//2)] if fit < float("inf")]
        if not survivors:
            survivors = [random_expr(2) for _ in range(2)]
        pop = survivors[:]
        while len(pop) < population:
            pop.append(mutate(random.choice(survivors)))
    return {"best_fitness": best[0], "best_expr": best[1], "best_meta": best[2], "history": history}

if __name__ == "__main__":
    r = evolve(3, 5)
    print(json.dumps({"best_fitness": r["best_fitness"], "best_expr": r["best_expr"], "history": r["history"]}, indent=2))
    
