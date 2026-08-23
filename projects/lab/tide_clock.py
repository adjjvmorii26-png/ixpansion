#!/usr/bin/env python3
"""Map integer ticks to a reproducible four-phase tidal clock."""
from __future__ import annotations
import argparse, json, math

PHASES=["slack","flood","high","ebb","low"]


def read(tick: int = 0) -> dict:
    cycle_position=(tick % 8 + 8) % 8
    phase=PHASES[int(cycle_position // 2)]
    height=round(math.sin(cycle_position * math.pi / 4), 6)
    return {"tick":tick,"phase":phase,"height":height,"direction":"incoming" if phase in ("flood","high") else "outgoing"}


def main(argv=None):
    parser=argparse.ArgumentParser(); parser.add_argument("tick", nargs="?", type=int, default=3)
    args=parser.parse_args(argv); print(json.dumps(read(args.tick), sort_keys=True)); return 0


if __name__ == "__main__": raise SystemExit(main())
