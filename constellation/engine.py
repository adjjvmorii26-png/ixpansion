"""Constellation Corpus — turn dispersed engine seeds into one integration plan."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from constellation.loom import render_loom, weave
except ModuleNotFoundError:
    from loom import render_loom, weave

DEFAULT_MANIFEST = Path(__file__).parent / "data" / "manifest.json"


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_manifest(path: Path | None = None) -> dict[str, Any]:
    manifest = json.loads((path or DEFAULT_MANIFEST).read_text(encoding="utf-8"))
    if manifest.get("schema") != "aleph.constellation.manifest.v1":
        raise ValueError("unsupported constellation manifest schema")
    repositories = manifest.get("repositories")
    if not isinstance(repositories, list) or not repositories:
        raise ValueError("constellation manifest has no repositories")
    required = {"name", "concept", "target", "files", "disk_kb", "version"}
    for repository in repositories:
        if not required.issubset(repository):
            raise ValueError(f"incomplete repository record: {repository.get('name')}")
    if len({item["name"] for item in repositories}) != len(repositories):
        raise ValueError("repository names must be unique")
    return manifest


def score_repository(repository: dict[str, Any]) -> dict[str, Any]:
    """Score conceptual value and adapter fit without network access."""
    files = int(repository["files"])
    disk_kb = int(repository["disk_kb"])
    density = round(min(1.0, files / max(1, disk_kb)), 4)
    structural_richness = min(30, files * 2)
    symbolic_payload = 10 if any(token in repository["concept"].lower() for token in ("memory", "paradox", "glyph", "focus")) else 5
    target_fit = 15 if "/" in repository["target"] else 8
    raw_score = 25 + structural_richness + symbolic_payload + target_fit + int(density * 20) + (len(repository["version"]) % 7)
    score = max(0, min(100, raw_score))
    classification = (
        "integrate_concept" if score >= 85
        else "prototype_adapter" if score >= 70
        else "preserve_reference"
    )
    return {
        "name": repository["name"],
        "target": repository["target"],
        "score": score,
        "classification": classification,
        "density": density,
        "resonance": f"{score}:{canonical_hash(repository)[:12]}",
    }


def plan(manifest: dict[str, Any] | None = None) -> dict[str, Any]:
    manifest = manifest or load_manifest()
    scored = sorted(
        (score_repository(item) for item in manifest["repositories"]),
        key=lambda item: (-item["score"], item["name"]),
    )
    integrated = sum(item["classification"] == "integrate_concept" for item in scored)
    adapters = sum(item["classification"] == "prototype_adapter" for item in scored)
    return {
        "experiment": "constellation-corpus",
        "engine_version": 1,
        "repositories": len(scored),
        "integrate_concept": integrated,
        "prototype_adapter": adapters,
        "preserve_reference": len(scored) - integrated - adapters,
        "recommendations": scored,
        "corpus_hash": canonical_hash([item["name"] + item["version"] for item in manifest["repositories"]]),
    }


def resonance_graph(manifest: dict[str, Any] | None = None) -> dict[str, Any]:
    manifest = manifest or load_manifest()
    nodes = []
    edges = []
    for repository in manifest["repositories"]:
        score = score_repository(repository)
        node_id = f"repo:{repository['name']}"
        target_id = f"target:{repository['target']}"
        nodes.extend([
            {"id": node_id, "kind": "repository", "label": repository["name"], "score": score["score"]},
            {"id": target_id, "kind": "target", "label": repository["target"]},
        ])
        edges.append({
            "source": node_id,
            "target": target_id,
            "relation": "concept_adapter",
            "weight": score["score"],
        })
    unique_nodes = {node["id"]: node for node in nodes}
    return {
        "nodes": list(unique_nodes.values()),
        "edges": sorted(edges, key=lambda edge: (-edge["weight"], edge["source"], edge["target"])),
        "graph_hash": canonical_hash(edges),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect the dispersed Constellation Corpus")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("plan")
    commands.add_parser("graph")
    weave_command = commands.add_parser("weave")
    weave_command.add_argument("--format", choices=("json", "markdown"), default="json")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        manifest = load_manifest(args.manifest)
        if args.command == "plan":
            result = plan(manifest)
        elif args.command == "graph":
            result = resonance_graph(manifest)
        else:
            result = weave(manifest)
            if args.format == "markdown":
                print(render_loom(result), end="")
                return 0
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
