"""Initialize the engine: create world state, spawn initial agents, seed data."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from nucleus.sandbox.world_state import WorldState


def main() -> None:
    world = WorldState()
    world.set_terrain((0, 0), "origin")
    for x in range(-5, 6):
        for y in range(-5, 6):
            world.set_terrain((x, y), "plains")

    print(f"World initialized: {len(world.terrain)} cells")
    print(f"Constants: {world.global_constants}")
    print(f"Snapshot: {world.snapshot()}")


if __name__ == "__main__":
    main()
