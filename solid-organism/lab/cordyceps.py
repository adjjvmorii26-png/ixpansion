#!/usr/bin/env python3
"""A consent-bounded cordyceps relay: refusals become immunity, never defeat."""
from __future__ import annotations

import argparse
import json
from typing import Any


def spread(hosts: list[dict[str, Any]], spores: list[str], generations: int = 4) -> dict[str, Any]:
    if generations < 0:
        raise ValueError("generations cannot be negative")
    by_id = {str(host["id"]): host for host in hosts}
    if len(by_id) != len(hosts):
        raise ValueError("host ids must be unique")
    if any(link not in by_id for host in hosts for link in host.get("links", [])):
        raise ValueError("all links must point to known hosts")
    if any(host_id not in by_id for host_id in spores):
        raise KeyError("spore origin is unknown")

    state = {host_id: "dormant" for host_id in by_id}
    expressed: set[str] = set()
    timeline: list[dict[str, int]] = []

    for host_id in spores:
        if by_id[host_id].get("consent") is True:
            state[host_id] = "expressing"
            expressed.add(host_id)
        else:
            state[host_id] = "immunity-memory"

    for generation in range(1, generations + 1):
        frontier = list(expressed)
        for host_id in frontier:
            for link in by_id[host_id].get("links", []):
                if state[link] != "dormant":
                    continue
                if by_id[link].get("consent") is True:
                    state[link] = "expressing"
                    expressed.add(link)
                else:
                    state[link] = "immunity-memory"
        timeline.append({
            "generation": generation,
            "expressing": len(expressed),
            "immunity_memory": list(state.values()).count("immunity-memory"),
        })

    return {
        "experiment": "consent-bounded-cordyceps",
        "generations": generations,
        "state": state,
        "timeline": timeline,
        "refusal_is_not_failure": True,
    }


def demo() -> dict[str, Any]:
    hosts = [
        {"id": "root", "consent": True, "links": ["willing", "boundary", "doubtful"]},
        {"id": "willing", "consent": True, "links": ["doubtful"]},
        {"id": "boundary", "consent": False, "links": []},
        {"id": "doubtful", "consent": False, "links": ["boundary"]},
    ]
    return spread(hosts, ["root"], 3)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the consent-bounded cordyceps model")
    parser.add_argument("--generations", type=int, default=3)
    args = parser.parse_args(argv)
    try:
        result = demo()
        result["generations"] = args.generations
        result["timeline"] = result["timeline"][:args.generations]
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (KeyError, TypeError, ValueError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
