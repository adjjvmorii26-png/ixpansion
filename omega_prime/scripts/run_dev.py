"""Development entry point: boots a lattice realm with sample agents."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from omega_prime.agents.registry import Registry
from omega_prime.agents.species.sentinel import Sentinel
from omega_prime.agents.species.wanderer import Wanderer
from omega_prime.sandbox.conductor import Conductor


def main() -> None:
    Registry.register("sentinel", Sentinel)
    Registry.register("wanderer", Wanderer)

    conductor = Conductor()
    conductor.enter("lattice", {"size": 8})

    scout = Registry.spawn("scout-01", "wanderer")
    guard = Registry.spawn("guard-01", "sentinel")

    for _ in range(5):
        obs = conductor.observation
        scout.observe(obs)
        guard.observe({"threat_level": 3})
        intents = [scout.deliberate(), guard.deliberate()]
        result = conductor.pulse(intents)
        print(f"pulse → {result}")

    conductor.exit()
    print("dev run complete")


if __name__ == "__main__":
    main()
