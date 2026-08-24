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


def _targets_overlap(first: str, second: str) -> bool:
    return first == second or first.startswith(f"{second}/") or second.startswith(f"{first}/")


def _conflict_map(threads: list[dict[str, Any]]) -> dict[str, list[str]]:
    return {
        thread["name"]: sorted(
            other["name"]
            for other in threads
            if other["name"] != thread["name"] and _targets_overlap(thread["target"], other["target"])
        )
        for thread in threads
    }


def _chaos(seed: str, phase: int, gate: str) -> float:
    try:
        from .engine import canonical_hash
    except ImportError:
        from engine import canonical_hash

    digest = canonical_hash([seed, phase, gate])
    return int(digest[:12], 16) / 0xFFFFFFFFFFFF


def rehearse(ritual: dict[str, Any] | None = None) -> dict[str, Any]:
    """Rehearse a ritual without touching targets; failures become rollback evidence."""
    if ritual is None:
        ritual = weave()
    if ritual.get("schema") != "aleph.constellation.ritual.v1":
        raise ValueError("unsupported constellation ritual schema")
    try:
        from .engine import canonical_hash
    except ImportError:
        from engine import canonical_hash

    conflicts = _conflict_map(ritual["threads"])
    wave_results = []
    rollback_ledger = []
    accounted: set[str] = set()

    for wave in ritual["waves"]:
        phase = wave["phase"]
        passed = []
        rolled_back = []
        quarantined = []
        events = []

        for name in wave["threads"]:
            thread = next(item for item in ritual["threads"] if item["name"] == name)
            accounted.add(name)
            linked = conflicts[name]
            restore_point = f"shadow:{thread['warp_signature']}"
            ledger_entry = {
                "thread": name,
                "phase": phase,
                "restore_point": restore_point,
                "strategy": "isolate overlapping target" if linked else "restore pre-wave projection",
            }
            rollback_ledger.append(ledger_entry)

            if linked:
                quarantined.append(name)
                events.append({
                    "thread": name,
                    "gate": "contract",
                    "status": "quarantined",
                    "reason": f"target overlap with {', '.join(linked)}",
                })
                continue

            failed_gate = None
            thresholds = {"contract": 1.0, "adapter": 0.82 - thread["score"] / 1000, "release": 0.88 - thread["score"] / 1000}
            for gate in ("contract", "adapter", "release"):
                if _chaos(thread["warp_signature"], phase, gate) >= thresholds[gate]:
                    failed_gate = gate
                    break

            if failed_gate is None:
                passed.append(name)
                events.append({"thread": name, "gate": "release", "status": "passed"})
            else:
                rolled_back.append(name)
                witness = canonical_hash([thread, failed_gate, restore_point])[:24]
                ledger_entry.update({"status": "rolled_back", "failed_gate": failed_gate, "witness": witness})
                events.append({
                    "thread": name,
                    "gate": failed_gate,
                    "status": "rolled_back",
                    "rollback_witness": witness,
                })

        wave_results.append({
            "phase": phase,
            "status": "quarantine_required" if quarantined else "ready",
            "passed": passed,
            "rolled_back": rolled_back,
            "quarantined": quarantined,
            "events": events,
        })

    collision_groups = [
        {"target": thread["target"], "threads": [thread["name"], *conflicts[thread["name"]]]}
        for thread in ritual["threads"]
        if conflicts[thread["name"]] and thread["name"] < min(conflicts[thread["name"]])
    ]
    return {
        "schema": "aleph.constellation.rehearsal.v1",
        "experiment": "ritual-shadow-rehearsal",
        "weave_hash": ritual["weave_hash"],
        "summary": {
            "threads": len(accounted),
            "passed": sum(len(wave["passed"]) for wave in wave_results),
            "rolled_back": sum(len(wave["rolled_back"]) for wave in wave_results),
            "quarantined": sum(len(wave["quarantined"]) for wave in wave_results),
            "collision_groups": len(collision_groups),
        },
        "waves": wave_results,
        "collision_groups": sorted(collision_groups, key=lambda group: (group["target"], group["threads"])),
        "rollback_ledger": rollback_ledger,
        "rehearsal_hash": canonical_hash([wave_results, rollback_ledger]),
    }


def render_rehearsal(rehearsal: dict[str, Any]) -> str:
    lines = [
        "# Constellation Shadow Rehearsal",
        "",
        f"Weave hash: `{rehearsal['weave_hash']}`",
        f"Rehearsal hash: `{rehearsal['rehearsal_hash']}`",
        "",
        "| Phase | Status | Passed | Rolled Back | Quarantined |",
        "|---|---|---:|---:|---:|",
    ]
    for wave in rehearsal["waves"]:
        lines.append(
            f"| {wave['phase']} | `{wave['status']}` | {len(wave['passed'])} "
            f"| {len(wave['rolled_back'])} | {len(wave['quarantined'])} |"
        )
    lines.extend(["", "## Rollback Ledger", ""])
    for entry in rehearsal["rollback_ledger"]:
        evidence = f"; witness `{entry['witness']}`" if entry.get("witness") else ""
        failure = f"; failed `{entry['failed_gate']}`" if entry.get("failed_gate") else ""
        lines.append(
            f"- Phase {entry['phase']} — **{entry['thread']}**: {entry['strategy']}{failure}{evidence}"
        )
    return "\n".join(lines) + "\n"


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
