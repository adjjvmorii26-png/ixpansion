"""Command-line rituals for observing MYCELIUM."""
from __future__ import annotations

import argparse
import json
from typing import Any

from mycelium.cognition.dream_compiler import DreamCompiler, build_demo_network
from mycelium.nucleus.substrate import ResourceSite, Substrate


def _serialize_sites(substrate: Substrate) -> list[dict[str, Any]]:
    return [
        {
            "site_id": site.site_id,
            "position": list(site.position),
            "nutrient": round(site.nutrient, 6),
            "reserve": site.reserve,
            "signal": round(site.signal, 6),
        }
        for site in substrate.ordered_sites()
    ]


def simulate(args: argparse.Namespace) -> dict[str, Any]:
    from mycelium.hyphae.hypha import Spore

    network = build_demo_network(args.seed, args.steps, args.sites)
    if args.spores > 1:
        for index in range(1, args.spores):
            angle = (index / args.spores) * 3.14159
            network.plant(
                Spore(
                    spore_id=f"ritual-spore-{index}",
                    genome={"curiosity": 0.22 + index * 0.04, "patience": 0.55 - index * 0.03},
                    viability=max(0.4, 0.78 - index * 0.04),
                ),
                position=(round(index * 0.13, 6), round(-index * 0.11, 6)),
            )
        for _ in range(args.steps):
            network.pulse()

    return {
        "experiment": "mycelium-pulse",
        "seed": args.seed,
        "steps": args.steps,
        "stats": network.stats,
        "sites": _serialize_sites(network.substrate),
        "recent_events": network.journal[-args.tail:],
    }


def dream(args: argparse.Namespace) -> dict[str, Any]:
    network = build_demo_network(args.seed, args.steps, args.sites)
    experiment = DreamCompiler().compile(network)
    if experiment is None:
        return {"dream": None, "reason": "no lived events available"}
    germination = network.plant(
        experiment.to_spore(), position=(0.18, -0.14)
    )
    return {
        "dream": experiment.payload(),
        "germinated_hypha_id": germination,
        "stats_after_planting": network.stats,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MYCELIUM living-runtime rituals")
    commands = parser.add_subparsers(dest="command", required=True)

    simulate_parser = commands.add_parser("simulate", help="run a consent-bounded pulse")
    simulate_parser.add_argument("--seed", type=int, default=42)
    simulate_parser.add_argument("--steps", type=int, default=6)
    simulate_parser.add_argument("--sites", type=int, default=5)
    simulate_parser.add_argument("--spores", type=int, default=1)
    simulate_parser.add_argument("--tail", type=int, default=8)
    simulate_parser.set_defaults(handler=simulate)

    dream_parser = commands.add_parser("dream", help="compile lived events into an experiment")
    dream_parser.add_argument("--seed", type=int, default=42)
    dream_parser.add_argument("--steps", type=int, default=8)
    dream_parser.add_argument("--sites", type=int, default=6)
    dream_parser.set_defaults(handler=dream)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.handler(args)
    except (ValueError, KeyError) as error:
        print(json.dumps({"error": str(error)}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
