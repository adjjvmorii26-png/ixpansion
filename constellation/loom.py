"""Ritual Loom — compile repository concepts into phased integration contracts."""
from __future__ import annotations

import json
from typing import Any


MAX_THREADS_PER_WAVE = 5


def _adapter_action(classification: str) -> str:
    return {
        "integrate_concept": "Fuse the concept into the target through a read-only projection",
        "prototype_adapter": "Prototype an isolated adapter behind a protocol boundary",
        "preserve_reference": "Archive the reference without runtime coupling",
    }[classification]


def weave(manifest: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        from .engine import canonical_hash, load_manifest, plan
    except ImportError:
        from engine import canonical_hash, load_manifest, plan

    manifest = manifest or load_manifest()
    recommendations = {
        item["name"]: item
        for item in plan(manifest)["recommendations"]
    }
    source_by_name = {item["name"]: item for item in manifest["repositories"]}
    threads = []

    for index, name in enumerate(sorted(source_by_name)):
        recommendation = recommendations[name]
        source = source_by_name[name]
        thread = {
            "name": name,
            "concept": source["concept"],
            "target": source["target"],
            "score": recommendation["score"],
            "classification": recommendation["classification"],
            "phase": index // MAX_THREADS_PER_WAVE + 1,
            "resonance": recommendation["resonance"],
            "gates": [
                {
                    "gate": "contract",
                    "action": f"Bind '{source['concept']}' to {source['target']}",
                },
                {
                    "gate": "adapter",
                    "action": _adapter_action(recommendation["classification"]),
                },
                {
                    "gate": "release",
                    "action": "Emit a deterministic witness and retain a rollback path",
                },
            ],
            "warp_signature": canonical_hash([source, recommendation])[:16],
        }
        threads.append(thread)

    wave_groups: dict[int, list[str]] = {}
    for thread in threads:
        wave_groups.setdefault(thread["phase"], []).append(thread["name"])
    waves = [
        {
            "phase": phase,
            "threads": wave_groups[phase],
            "quorum": "contract, adapter, and release gates must pass",
        }
        for phase in sorted(wave_groups)
    ]

    return {
        "schema": "aleph.constellation.ritual.v1",
        "experiment": "ritual-loom",
        "threads": threads,
        "waves": waves,
        "policy": {
            "max_threads_per_wave": MAX_THREADS_PER_WAVE,
            "safety": [
                "read-only projections precede mutation",
                "every release emits a deterministic witness",
                "adapters remain reversible during prototyping",
            ],
        },
        "weave_hash": canonical_hash(threads),
    }


def render_loom(ritual: dict[str, Any]) -> str:
    lines = [
        "# Constellation Ritual Loom",
        "",
        f"Weave hash: `{ritual['weave_hash']}`",
        "",
    ]
    waves_by_phase = {wave["phase"]: wave for wave in ritual["waves"]}
    for thread in ritual["threads"]:
        wave = waves_by_phase[thread["phase"]]
        lines.extend([
            f"## Phase {thread['phase']} — {thread['name']}",
            "",
            f"- Wave quorum: {wave['quorum']}",
            f"- Concept: {thread['concept']}",
            f"- Target: `{thread['target']}`",
            f"- Classification: `{thread['classification']}` ({thread['score']}/100)",
            "- Gates:",
            *[f"  - {gate['gate'].title()}: {gate['action']}" for gate in thread["gates"]],
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"
