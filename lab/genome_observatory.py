#!/usr/bin/env python3
"""Genome Observatory — sealed lineage census, diversity map, and pair guidance."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from html import escape
from typing import Any

from lab.mandate_genome import (
    COMPATIBILITY_RADIUS,
    MAX_GENERATION,
    SCHEMA as GENOME_SCHEMA,
    _clamp,
    _compatibility,
    load_genomes,
)
from lab.runtime_vault import path, read_json, report_path, write_json


SCHEMA = "aleph.chronoforge.genome-observatory.v1"
TRAITS = ("risk_appetite", "patience", "curiosity", "conservation", "resilience")
POLICIES = ("ration", "stabilize", "expand")
OUTCOME_COLORS = {
    "successful": "#38bdf8",
    "dream": "#c084fc",
    "quarantined": "#fb7185",
    "synthesized": "#a3e635",
}


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(payload: Any) -> str:
    return hashlib.sha256(_canonical(payload)).hexdigest()


def _ancestors(identifier: str, by_id: dict[str, dict[str, Any]]) -> set[str]:
    found: set[str] = set()
    stack = list(by_id[identifier].get("parent_ids", []))
    while stack:
        current = stack.pop()
        if current in found:
            continue
        found.add(current)
        stack.extend(by_id[current].get("parent_ids", []))
    return found


def _descendants(identifier: str, by_id: dict[str, dict[str, Any]]) -> set[str]:
    children: dict[str, set[str]] = defaultdict(set)
    for genome in by_id.values():
        for parent in genome.get("parent_ids", []):
            children[parent].add(genome["genome_id"])
    found: set[str] = set()
    stack = list(children[identifier])
    while stack:
        current = stack.pop()
        if current in found:
            continue
        found.add(current)
        stack.extend(children[current])
    return found


def _validate_population(genomes: list[dict[str, Any]]) -> None:
    identifiers = [item.get("genome_id") for item in genomes]
    if any(not identifier for identifier in identifiers) or len(identifiers) != len(set(identifiers)):
        raise ValueError("genome identifiers are missing or duplicated")
    by_id = {item["genome_id"]: item for item in genomes}
    for genome in genomes:
        if genome.get("schema") != GENOME_SCHEMA:
            raise ValueError(f"genome {genome.get('genome_id', '<unknown>')} has an unsupported schema")
        parents = genome.get("parent_ids", [])
        expected_parents = 0 if int(genome.get("generation", 0)) == 1 else 2
        if len(parents) != expected_parents:
            raise ValueError(f"genome {genome['genome_id']} has an invalid parent count")
        if any(parent not in by_id for parent in parents):
            raise ValueError(f"genome {genome['genome_id']} references an unknown ancestor")
        if any(int(by_id[parent]["generation"]) >= int(genome["generation"]) for parent in parents):
            raise ValueError(f"genome {genome['genome_id']} does not descend forward in time")


def _diversity(genomes: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(genomes)
    policy_counts = Counter(item.get("policy", "unknown") for item in genomes)
    probabilities = [value / total for value in policy_counts.values() if value]
    raw_entropy = -sum(value * math.log2(value) for value in probabilities)
    maximum_entropy = math.log2(max(len(probabilities), 1))
    normalized_entropy = raw_entropy / maximum_entropy if maximum_entropy else 0.0
    return {
        "policy_entropy": round(normalized_entropy, 5),
        "effective_policies": round(2 ** raw_entropy, 3),
        "trait_ranges": {
            name: round(
                max(float(item["traits"][name]) for item in genomes)
                - min(float(item["traits"][name]) for item in genomes),
                5,
            )
            for name in TRAITS
        }
        if genomes
        else {name: 0.0 for name in TRAITS},
    }


def _compatible_pairs(genomes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    eligible = sorted(
        (item for item in genomes if item.get("breedable") is True),
        key=lambda item: item["genome_id"],
    )
    by_id = {item["genome_id"]: item for item in genomes}
    pairs = []
    for index, first in enumerate(eligible):
        first_family = _ancestors(first["genome_id"], by_id) | _descendants(first["genome_id"], by_id) | {first["genome_id"]}
        for second in eligible[index + 1:]:
            compatibility = _compatibility(first, second)
            second_family = _ancestors(second["genome_id"], by_id) | _descendants(second["genome_id"], by_id) | {second["genome_id"]}
            if compatibility >= 1.0 - COMPATIBILITY_RADIUS:
                pairs.append({
                    "parent_ids": [first["genome_id"], second["genome_id"]],
                    "compatibility": compatibility,
                    "related": bool(first_family & second_family),
                    "parents": [first, second],
                })
    return pairs


def _recommendations(genomes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    recommendations = []
    for pair in _compatible_pairs(genomes):
        if pair["related"]:
            continue
        left, right = pair["parents"]
        average_resilience = (
            float(left["traits"]["resilience"]) + float(right["traits"]["resilience"])
        ) / 2
        policy_diversity = 1.0 if left["policy"] != right["policy"] else 0.25
        spreads = [
            abs(float(left["traits"][name]) - float(right["traits"][name]))
            for name in TRAITS
        ]
        complementarity = sum(spreads) / len(spreads)
        priority = (
            0.45 * float(pair["compatibility"])
            + 0.25 * average_resilience
            + 0.20 * policy_diversity
            + 0.10 * complementarity
        )
        traits = {
            name: _clamp((float(left["traits"][name]) + float(right["traits"][name])) / 2)
            for name in left["traits"]
        }
        differentiation = _clamp((1.0 - float(pair["compatibility"])) * 0.08)
        traits["risk_appetite"] = _clamp(traits["risk_appetite"] + differentiation)
        projected_policy = min(
            POLICIES,
            key=lambda policy: (
                abs({"ration": 0.20, "stabilize": 0.55, "expand": 0.90}[policy] - traits["risk_appetite"]),
                policy,
            ),
        )
        recommendations.append({
            "parent_ids": pair["parent_ids"],
            "compatibility": float(pair["compatibility"]),
            "priority": _clamp(priority),
            "projected_policy": projected_policy,
            "projected_traits": traits,
            "rationale": (
                "unrelated lineages with compatible bounds"
                if policy_diversity == 1.0
                else "compatible same-policy lineages; monitor monoculture"
            ),
        })
    return sorted(recommendations, key=lambda item: (-item["priority"], item["parent_ids"]))[:3]


def census(genomes: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Build a sealed read-only model of the current genome population."""
    population = load_genomes() if genomes is None else genomes
    _validate_population(population)
    outcome_counts = Counter(item.get("outcome", "unknown") for item in population)
    policy_counts = Counter(item.get("policy", "unknown") for item in population)
    generation_counts = Counter(int(item.get("generation", 0)) for item in population)
    breedable_count = sum(item.get("breedable") is True for item in population)

    warnings = []
    if not population:
        warnings.append({"kind": "empty_population", "detail": "no verified genomes are available"})
    if breedable_count < 2:
        warnings.append({"kind": "insufficient_breeding_pool", "detail": "fewer than two successful genomes"})
    if population and max(policy_counts.values(), default=0) / len(population) >= 0.80:
        dominant = policy_counts.most_common(1)[0][0]
        warnings.append({"kind": "policy_monoculture", "detail": f"{dominant} dominates the population"})
    for name, spread in (_diversity(population)["trait_ranges"].items() if population else []):
        if len(population) >= 2 and spread <= 0.05:
            warnings.append({"kind": "narrow_trait_range", "detail": name})
    max_generation = max(generation_counts, default=0)
    if max_generation >= MAX_GENERATION - 1:
        warnings.append({"kind": "generation_ceiling_pressure", "detail": str(max_generation)})

    stable = {
        "schema": SCHEMA,
        "experiment": "genome-observatory",
        "status": "sealed",
        "population": {
            "total": len(population),
            "breedable": breedable_count,
            "outcome_counts": dict(sorted(outcome_counts.items())),
            "policy_counts": dict(sorted(policy_counts.items())),
            "generation_counts": {str(key): value for key, value in sorted(generation_counts.items())},
            "maximum_generation": max_generation,
        },
        "diversity": _diversity(population),
        "genomes": [
            {
                "genome_id": item["genome_id"],
                "sigil": item.get("sigil", ""),
                "policy": item.get("policy", "unknown"),
                "generation": int(item.get("generation", 0)),
                "outcome": item.get("outcome", "unknown"),
                "breedable": item.get("breedable") is True,
            }
            for item in sorted(population, key=lambda item: item["genome_id"])
        ],
        "lineages": [
            {"child_id": item["genome_id"], "parent_ids": list(item.get("parent_ids", []))}
            for item in sorted(population, key=lambda item: item["genome_id"])
        ],
        "compatibilities": [
            {key: value for key, value in pair.items() if key != "parents"}
            for pair in _compatible_pairs(population)
        ],
        "warnings": warnings,
        "recommendations": _recommendations(population),
        "source_schema": GENOME_SCHEMA,
    }
    stable["census_hash"] = _hash(stable)
    return stable


def _position(index: int, total: int) -> tuple[float, float]:
    if total == 1:
        return 480.0, 320.0
    angle = (2 * math.pi * index / total) - math.pi / 2
    radius = 180 + 22 * (index % 3)
    return 480.0 + radius * math.cos(angle), 330.0 + radius * math.sin(angle)


def render_observatory(census_report: dict[str, Any]) -> str:
    """Render the sealed census as dependency-free HTML/SVG."""
    body = {key: value for key, value in census_report.items() if key != "census_hash"}
    if census_report.get("status") != "sealed" or census_report.get("census_hash") != _hash(body):
        raise ValueError("observatory census is missing, unsealed, or modified")

    genomes = census_report.get("genomes", [])
    by_id = {item["genome_id"]: item for item in genomes}
    if len(by_id) != len(genomes):
        raise ValueError("observatory snapshot contains duplicate genome identities")
    ordered_ids = sorted(
        by_id,
        key=lambda identifier: (-int(by_id[identifier]["generation"]), identifier),
    )
    positions = {
        identifier: _position(index, len(ordered_ids))
        for index, identifier in enumerate(ordered_ids)
    }

    def edge(x1: float, y1: float, x2: float, y2: float, className: str) -> str:
        return f'<line class="{className}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.2f}" y2="{y2:.1f}" />'

    lineage_lines = []
    for edge_item in census_report["lineages"]:
        child = edge_item["child_id"]
        for parent in edge_item["parent_ids"]:
            x1, y1 = positions[parent]
            x2, y2 = positions[child]
            lineage_lines.append(edge(x1, y1, x2, y2, "lineage"))
    compatibility_lines = []
    for pair in census_report["compatibilities"]:
        first, second = pair["parent_ids"]
        x1, y1 = positions[first]
        x2, y2 = positions[second]
        compatibility_lines.append(edge(x1, y1, x2, y2, "compatibility"))

    nodes = []
    for identifier in ordered_ids:
        item = by_id[identifier]
        x, y = positions[identifier]
        color = OUTCOME_COLORS.get(item.get("outcome"), "#94a3b8")
        nodes.append(
            '<g class="node"><circle cx="{x:.1f}" cy="{y:.1f}" r="19" fill="{color}" />'
            '<text class="label" x="{x:.1f}" y="{y:.1f}">{sigil}</text>'
            '<text class="meta" x="{x:.1f}" y="{below:.1f}">{identity}</text></g>'.format(
                x=x, y=y, below=y + 34, color=escape(color),
                sigil=escape(str(item.get("sigil", ""))),
                identity=escape(f"G{item['generation']} · {item['policy']}"),
            )
        )

    warning_items = "".join(
        f"<li><strong>{escape(item['kind'])}</strong> — {escape(item['detail'])}</li>"
        for item in census_report["warnings"]
    ) or "<li>No active population warnings.</li>"
    recommendation_items = "".join(
        "<li><strong>{parents}</strong> · priority {priority:.3f} → {policy}"
        "<small>{rationale}</small></li>".format(
            parents=escape(" × ".join(item["parent_ids"])),
            priority=float(item["priority"]),
            policy=escape(item["projected_policy"]),
            rationale=escape(item["rationale"]),
        )
        for item in census_report["recommendations"]
    ) or "<li>No unrelated compatible pairing is currently available.</li>"
    metric_items = "".join(
        f"<tr><th>{escape(key.replace('_', ' ').title())}</th><td>{escape(str(value))}</td></tr>"
        for key, value in census_report["population"].items()
    )
    diversity_items = "".join(
        f"<tr><th>{escape(key.replace('_', ' ').title())}</th><td>{escape(str(value))}</td></tr>"
        for key, value in census_report["diversity"].items()
    )

    return '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Genome Observatory</title>
<style>
:root {{ color-scheme: dark; --ink:#e2e8f0; --muted:#94a3b8; --panel:#101827; }}
* {{ box-sizing:border-box }} body {{ margin:0;background:#070b14;color:var(--ink);font-family:ui-sans-serif,system-ui,sans-serif }}
header,main {{ max-width:1080px;margin:auto;padding:24px }} h1,h2 {{ font-family:ui-serif,Georgia,serif }}
.lede {{ color:var(--muted) }} .grid {{ display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px }}
.panel,.map {{ background:var(--panel);border:1px solid #223047;border-radius:14px;padding:16px }}
svg {{ width:100%;height:auto }} .lineage {{ stroke:#334155;stroke-width:2 }} .compatibility {{ stroke:#38bdf8;stroke-opacity:.32;stroke-dasharray:5 7 }}
circle {{ stroke:#e2e8f0;stroke-width:1 }} text {{ fill:#e2e8f0;text-anchor:middle;font-size:11px }} .meta {{ fill:#94a3b8;font-size:9px }}
ul {{ padding-left:20px }} li {{ margin:8px 0 }} li strong {{ color:#7dd3fc }} small {{ display:block;color:var(--muted) }}
table {{ width:100%;border-collapse:collapse }} th,td {{ border-bottom:1px solid #223047;padding:7px;text-align:left }} th {{ color:#94a3b8 }}
footer {{ max-width:1080px;margin:auto;padding:12px 24px 36px;color:var(--muted) }}
</style>
</head>
<body>
<header><p class="lede">ALEPH · Chrono Forge heredity</p><h1>Genome Observatory</h1>
<p class="lede">Read-only ancestry, diversity pressure, and consent-bounded pairing guidance.</p></header>
<main>
<svg viewBox="0 0 960 660" role="img" aria-label="Radial mandate genome lineage map">
{lineage}{compatibility}{nodes}
</svg>
<div class="grid">
<section class="panel"><h2>Population</h2><table><tbody>{metrics}</tbody></table></section>
<section class="panel"><h2>Diversity</h2><table><tbody>{diversity}</tbody></table></section>
<section class="panel"><h2>Warnings</h2><ul>{warnings}</ul></section>
<section class="panel"><h2>Recommended Pairings</h2><ul>{recommendations}</ul></section>
</div>
</main>
<footer>Census <code>{census_hash}</code> · sealed read-only evidence</footer>
<script>void(0)</script>
</body></html>
'''.format(
        lineage="".join(lineage_lines),
        compatibility="".join(compatibility_lines),
        nodes="".join(nodes),
        metrics=metric_items,
        diversity=diversity_items,
        warnings=warning_items,
        recommendations=recommendation_items,
        census_hash=escape(census_report["census_hash"]),
    )


def write_observatory(census_report: dict[str, Any], output: Path | None = None) -> dict[str, Any]:
    target = output or path("atlas", "genome-observatory.html")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_observatory(census_report), encoding="utf-8")
    return {"ok": True, "output": str(target), "census_hash": census_report["census_hash"]}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("census", help="seal and persist a fresh census")
    atlas = commands.add_parser("atlas", help="render an HTML/SVG observatory")
    atlas.add_argument("--report", type=Path, default=None)
    atlas.add_argument("--output", type=Path, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "census":
            result = census()
            write_json(report_path("genome-observatory.json"), result)
        else:
            source = args.report or report_path("genome-observatory.json")
            result = write_observatory(read_json(source, {}), args.output)
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (KeyError, TypeError, ValueError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, sort_keys=True, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
