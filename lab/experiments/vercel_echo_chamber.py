"""Vercel Echo Chamber — Recursive self-observation via API introspection.

The echo chamber reads the API endpoints' source code, analyzes their structure,
and generates a meta-observation about the system's self-awareness capabilities.
It then "echoes" this observation back as a synthetic module that describes itself.
"""
from __future__ import annotations
import hashlib
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class EchoChamber:
    """A recursive self-observation system."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.observations = []
        self.echo_depth = 0
        self.max_depth = 5

    def observe_api_layer(self) -> dict:
        """Read and analyze all API endpoint source files."""
        api_dir = ROOT / "api"
        endpoints = []
        if api_dir.exists():
            for py in api_dir.glob("*.py"):
                if py.name.startswith("_"):
                    continue
                text = py.read_text(errors="replace")
                lines = text.splitlines()
                functions = [
                    ln.strip().split("(")[0].replace("def ", "")
                    for ln in lines
                    if ln.strip().startswith("def ")
                ]
                endpoints.append({
                    "name": py.stem,
                    "functions": functions,
                    "lines": len(lines),
                    "hash": hashlib.md5(text.encode()).hexdigest()[:8],
                })

        return {
            "endpoint_count": len(endpoints),
            "endpoints": endpoints,
            "total_functions": sum(len(ep["functions"]) for ep in endpoints),
            "observation_time": time.time(),
        }

    def echo(self, observation: dict, depth: int = 0) -> dict:
        """Recursively echo an observation, creating meta-observations."""
        if depth >= self.max_depth:
            return {"depth": depth, "message": "echo reached maximum depth", "sealed": True}

        # Generate a meta-observation about the observation
        obs_hash = hashlib.sha256(json.dumps(observation, default=str).encode()).hexdigest()[:12]
        meta = {
            "depth": depth,
            "observed_hash": obs_hash,
            "observation_type": type(observation).__name__,
            "echo_seed": (self.seed + depth * 7) % 1000,
            "self_reference": f"echo_depth_{depth}_observes_{len(self.observations)}_prior",
            "timestamp": time.time(),
        }

        self.observations.append(meta)

        # Recursive echo on the meta-observation
        return self.echo(meta, depth + 1)

    def run(self) -> dict:
        """Execute the full echo chamber cycle."""
        observation = self.observe_api_layer()
        echo_result = self.echo(observation)

        # Synthesize the echo chamber's self-assessment
        depth_reached = echo_result.get("depth", 0) if isinstance(echo_result, dict) else self.max_depth
        return {
            "chamber": "vercel_echo_chamber",
            "api_observation": observation,
            "echo_result": echo_result,
            "total_observations": len(self.observations),
            "depth_reached": depth_reached,
            "self_assessment": (
                f"Observed {observation['endpoint_count']} API endpoints "
                f"with {observation['total_functions']} functions. "
                f"Echoed to depth {depth_reached}. "
                f"The system demonstrates {len(self.observations)} layers of self-reference."
            ),
            "verdict": "self_aware" if depth_reached >= 3 else "proto_aware",
        }


def demo():
    chamber = EchoChamber(seed=42)
    return chamber.run()


def main():
    import json as _json
    result = demo()
    print(_json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
