#!/usr/bin/env python3
"""
IXPANSION JS / Lattice Simulation Hook
Runs Node.js lattice simulations and returns structured results
for local agents and secure remote handoff.
"""

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from a2a_capability_cards import CapabilityCard, bootstrap_registry
from event_driven_sync import bus, store

SIM_DIR = Path(__file__).resolve().parent / "simulations"
LATTICE_JS = SIM_DIR / "ixpansion_lattice.js"


def node_available() -> bool:
    return shutil.which("node") is not None


def run_ixpansion_lattice(
    n: int = 16,
    steps: int = 30,
    seed: float = 0.5,
    timeout: float = 30.0,
) -> Dict[str, Any]:
    if not LATTICE_JS.exists():
        return {"error": f"missing {LATTICE_JS}"}
    if not node_available():
        # pure-python fallback (coarse)
        return _python_lattice_fallback(n=n, steps=steps, seed=seed)

    payload = json.dumps({"n": n, "steps": steps, "seed": seed})
    try:
        proc = subprocess.run(
            ["node", str(LATTICE_JS), payload],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(SIM_DIR),
        )
        if proc.returncode != 0:
            return {"error": proc.stderr[:500] or "node failed", "code": proc.returncode}
        return json.loads(proc.stdout)
    except subprocess.TimeoutExpired:
        return {"error": "simulation timeout"}
    except Exception as e:
        return {"error": str(e)}


def _python_lattice_fallback(n: int, steps: int, seed: float) -> Dict[str, Any]:
    import math
    grid = [math.sin((i + seed * 100) * 0.17) * 0.5 for i in range(n * n)]
    history = []
    for t in range(steps):
        nxt = grid[:]
        energy = 0.0
        for x in range(n):
            for y in range(n):
                i = x * n + y
                neigh = (
                    grid[((x + 1) % n) * n + y]
                    + grid[((x - 1) % n) * n + y]
                    + grid[x * n + (y + 1) % n]
                    + grid[x * n + (y - 1) % n]
                )
                val = 0.98 * (grid[i] * 0.5 + neigh * 0.125) + 0.02 * math.sin(t * 0.1 + seed)
                nxt[i] = val
                energy += val * val
        grid = nxt
        history.append(round(energy, 6))
    return {
        "type": "ixpansion_lattice",
        "n": n,
        "steps": steps,
        "seed": seed,
        "final_energy": history[-1],
        "energy_history": history[-20:],
        "engine": "python_fallback",
    }


class IXPansionExecutor:
    def __init__(self):
        self.agent_id = "ixpansion"
        reg = bootstrap_registry()
        reg.register(CapabilityCard(
            agent_id=self.agent_id,
            name="IXPANSION Lattice Engine",
            description="Runs JS lattice / cellular simulations (Node) with Python fallback",
            capabilities=[
                "ixpansion", "lattice_js", "cellular", "simulation", "physics"
            ],
            version="0.2.0",
        ))
        store.update_agent(self.agent_id, {
            "status": "online",
            "node": node_available(),
        })

    def run(self, kind: str = "lattice", params: Optional[Dict] = None) -> Dict[str, Any]:
        params = params or {}
        if kind in ("lattice", "ixpansion", "lattice_js", "cellular", "simulation", "physics"):
            result = run_ixpansion_lattice(
                n=int(params.get("n", 16)),
                steps=int(params.get("steps", 30)),
                seed=float(params.get("seed", 0.5)),
            )
            bus.publish("simulation.ixpansion", result)
            return result
        return {"error": f"unknown kind {kind}"}


def execute_ixpansion_capability(capability: str, payload: dict) -> dict:
    return IXPansionExecutor().run(payload.get("kind", capability), payload)


if __name__ == "__main__":
    ex = IXPansionExecutor()
    r = ex.run("lattice", {"n": 12, "steps": 20, "seed": 0.3})
    print(json.dumps({k: r[k] for k in r if k != "snapshot"}, indent=2))
  
