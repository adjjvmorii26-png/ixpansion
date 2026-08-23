#!/usr/bin/env python3
"""Split a belief lattice into factions while preserving a treaty path."""
from __future__ import annotations
import argparse, hashlib, json


def schism(nodes: list[dict], threshold: float = 0.55) -> dict:
    if threshold < 0 or threshold > 1:
        raise ValueError("threshold must be between 0 and 1")
    dawn = [node["id"] for node in nodes if float(node.get("coherence", 0)) >= threshold]
    dusk = [node["id"] for node in nodes if float(node.get("coherence", 0)) < threshold]
    overlap = sorted(set(dawn) & set(dusk))
    return {
        "dawn": dawn,
        "dusk": dusk,
        "treaty_possible": bool(dawn and dusk),
        "overlap": overlap,
        "treaty_hash": hashlib.sha256(json.dumps([dawn, dusk], sort_keys=True).encode()).hexdigest()[:16],
    }


def demo(): return schism([
    {"id":"keystone","coherence":.82}, {"id":"lantern","coherence":.61},
    {"id":"moth","coherence":.34}, {"id":"salt","coherence":.12},
])


def main(argv=None):
    parser=argparse.ArgumentParser(); parser.add_argument("--threshold", type=float, default=.55)
    args=parser.parse_args(argv)
    try: print(json.dumps(demo(), sort_keys=True))
    except ValueError as error: print(json.dumps({"ok":False,"error":str(error)})); return 1
    return 0


if __name__ == "__main__": raise SystemExit(main())
