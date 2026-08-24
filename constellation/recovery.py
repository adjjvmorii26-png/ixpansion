"""Recovery Braids — isolate collisions and schedule witnessed retry orbits."""
from __future__ import annotations

from typing import Any


MAX_RETRY_ATTEMPTS = 3


def _targets_overlap(first: str, second: str) -> bool:
    return first == second or first.startswith(f"{second}/") or second.startswith(f"{first}/")


def _common_root(targets: list[str]) -> str:
    components = [target.strip("/").split("/") for target in targets]
    prefix = []
    for index, value in enumerate(components[0]):
        if any(index >= len(item) or item[index] != value for item in components[1:]):
            break
        prefix.append(value)
    return "/".join(prefix) or "virtual/braid"


def _collision_components(threads: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    names = [thread["name"] for thread in threads]
    parent = {name: name for name in names}

    def find(name: str) -> str:
        while parent[name] != name:
            parent[name] = parent[parent[name]]
            name = parent[name]
        return name

    def union(first: str, second: str) -> None:
        first_root = find(first)
        second_root = find(second)
        if first_root != second_root:
            parent[max(first_root, second_root)] = min(first_root, second_root)

    for left in threads:
        for right in threads:
            if left["name"] < right["name"] and _targets_overlap(left["target"], right["target"]):
                union(left["name"], right["name"])

    groups: dict[str, list[dict[str, Any]]] = {}
    for thread in threads:
        groups.setdefault(find(thread["name"]), []).append(thread)
    return [sorted(group, key=lambda item: item["name"]) for group in groups.values()]


def recover(ritual: dict[str, Any] | None = None, rehearsal: dict[str, Any] | None = None) -> dict[str, Any]:
    """Turn rehearsal quarantines and rollbacks into isolated recovery work."""
    try:
        from .engine import canonical_hash
        from .loom import rehearse, weave
    except ImportError:
        from engine import canonical_hash
        from loom import rehearse, weave

    ritual = ritual or weave()
    rehearsal = rehearsal or rehearse(ritual)
    if ritual.get("schema") != "aleph.constellation.ritual.v1":
        raise ValueError("unsupported constellation ritual schema")
    if rehearsal.get("schema") != "aleph.constellation.rehearsal.v1":
        raise ValueError("unsupported constellation rehearsal schema")

    threads = {thread["name"]: thread for thread in ritual["threads"]}
    collision_threads = [
        thread
        for wave in rehearsal["waves"]
        for thread in (threads[name] for name in wave["quarantined"])
    ]

    braids = []
    covered_quarantines: set[str] = set()
    for members in sorted(_collision_components(collision_threads), key=lambda group: group[0]["name"]):
        member_names = {member["name"] for member in members}
        covered_quarantines.update(member_names)
        root = _common_root([member["target"] for member in members])
        braid_id = canonical_hash([root, sorted(member_names)])[:16]
        lanes = []
        for sequence, member in enumerate(sorted(members, key=lambda item: (-item["score"], item["name"])), 1):
            lane_target = f"braid/{braid_id}/{member['name']}"
            lanes.append({
                "sequence": sequence,
                "thread": member["name"],
                "original_target": member["target"],
                "isolated_target": lane_target,
                "boundary": "canonical event envelope with per-lane schema",
            })
        braids.append({
            "braid_id": braid_id,
            "shared_root": root,
            "lanes": lanes,
            "bridge": "all lanes publish through one reversible braid bus",
            "braid_hash": canonical_hash(lanes),
        })

    rollback_entries = {
        entry["thread"]: entry
        for entry in rehearsal["rollback_ledger"]
        if entry.get("status") == "rolled_back"
    }
    remedies = {
        "contract": "Rebind a narrower contract against the preserved shadow projection",
        "adapter": "Split the adapter behind an explicit protocol boundary",
        "release": "Stage a lower-entropy shadow release before promotion",
    }
    orbits = []
    for name in sorted(rollback_entries):
        entry = rollback_entries[name]
        orbit_id = canonical_hash([entry["witness"], MAX_RETRY_ATTEMPTS])[:16]
        attempts = [
            {
                "attempt": attempt,
                "remedy": remedies[entry["failed_gate"]],
                "decay": round(0.82 ** (attempt - 1), 4),
                "promotion": f"match witness {entry['witness']} under reduced chaos",
            }
            for attempt in range(1, MAX_RETRY_ATTEMPTS + 1)
        ]
        orbits.append({
            "orbit_id": orbit_id,
            "thread": name,
            "phase": entry["phase"],
            "failed_gate": entry["failed_gate"],
            "restore_point": entry["restore_point"],
            "max_attempts": MAX_RETRY_ATTEMPTS,
            "attempts": attempts,
            "orbit_hash": canonical_hash(attempts),
        })

    return {
        "schema": "aleph.constellation.recovery.v1",
        "experiment": "recovery-braids",
        "weave_hash": ritual["weave_hash"],
        "rehearsal_hash": rehearsal["rehearsal_hash"],
        "summary": {
            "braids": len(braids),
            "lanes": sum(len(braid["lanes"]) for braid in braids),
            "quarantined_covered": len(covered_quarantines),
            "retry_orbits": len(orbits),
            "max_retry_attempts": MAX_RETRY_ATTEMPTS,
        },
        "braids": sorted(braids, key=lambda item: item["braid_id"]),
        "retry_orbits": orbits,
        "recovery_hash": canonical_hash([braids, orbits]),
    }


def render_recovery(recovery: dict[str, Any]) -> str:
    lines = [
        "# Constellation Recovery Braids",
        "",
        f"Rehearsal hash: `{recovery['rehearsal_hash']}`",
        f"Recovery hash: `{recovery['recovery_hash']}`",
        "",
        "## Isolated Collision Braids",
        "",
    ]
    for braid in recovery["braids"]:
        lines.extend([
            f"### Braid `{braid['braid_id']}` — `{braid['shared_root']}`",
            "",
        ])
        for lane in braid["lanes"]:
            lines.append(
                f"- **{lane['thread']}** → `{lane['isolated_target']}` "
                f"(from `{lane['original_target']}`, sequence {lane['sequence']})"
            )
        lines.append("")
    lines.extend(["## Witnessed Retry Orbits", ""])
    for orbit in recovery["retry_orbits"]:
        lines.extend([
            f"### `{orbit['thread']}` — failed `{orbit['failed_gate']}`",
            "",
            f"- Restore point: `{orbit['restore_point']}`",
            *[f"- Attempt {attempt['attempt']}: {attempt['remedy']} (decay {attempt['decay']})" for attempt in orbit["attempts"]],
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"
