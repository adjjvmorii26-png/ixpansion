"""Lane Treaties — negotiate reversible boundaries between recovery lanes."""
from __future__ import annotations

from typing import Any


TREATY_PROTOCOL = "aleph.lane-treaty.v1"


def _party_context(recovery: dict[str, Any], thread: str) -> dict[str, Any]:
    lane = next(
        item
        for braid in recovery["braids"]
        for item in braid["lanes"]
        if item["thread"] == thread
    )
    orbit = next(
        (item for item in recovery["retry_orbits"] if item["thread"] == thread),
        None,
    )
    context = {
        "thread": thread,
        "isolated_target": lane["isolated_target"],
        "original_target": lane["original_target"],
    }
    if orbit:
        context["memory"] = {
            "failed_gate": orbit["failed_gate"],
            "restore_point": orbit["restore_point"],
            "max_retry_attempts": orbit["max_attempts"],
        }
    else:
        context["memory"] = {"state": "clean-shadow"}
    return context


def negotiate(recovery: dict[str, Any] | None = None) -> dict[str, Any]:
    """Ratify pairwise boundaries for every lane sharing a collision braid."""
    try:
        from .engine import canonical_hash
        from .recovery import recover
    except ImportError:
        from engine import canonical_hash
        from recovery import recover

    recovery = recovery or recover()
    if recovery.get("schema") != "aleph.constellation.recovery.v1":
        raise ValueError("unsupported constellation recovery schema")

    treaties = []
    for braid in recovery["braids"]:
        parties = sorted(
            (_party_context(recovery, lane["thread"]) for lane in braid["lanes"]),
            key=lambda item: item["thread"],
        )
        for left_index, left in enumerate(parties):
            for right in parties[left_index + 1 :]:
                pair = sorted((left["thread"], right["thread"]))
                targets = sorted((left["isolated_target"], right["isolated_target"]))
                noninterference = len(set(targets)) == 2
                clauses = [
                    {
                        "clause": "namespace_partition",
                        "terms": f"{left['thread']} owns {left['isolated_target']}; {right['thread']} owns {right['isolated_target']}",
                        "consent": left["isolated_target"] != right["isolated_target"],
                    },
                    {
                        "clause": "event_lease",
                        "terms": f"both lanes lease braid bus {braid['braid_id']} through canonical envelopes only",
                        "consent": bool(braid["bridge"]),
                    },
                    {
                        "clause": "witness_exchange",
                        "terms": "each release publishes its deterministic witness before the next lane promotes",
                        "consent": True,
                    },
                    {
                        "clause": "rollback_noninterference",
                        "terms": "one lane's rollback restores only its own shadow projection",
                        "consent": noninterference,
                    },
                    {
                        "clause": "arbitration",
                        "terms": f"{pair[0]} arbitrates stale leases; {pair[1]} arbitrates schema collisions",
                        "consent": pair[0] != pair[1],
                    },
                ]
                memories = {
                    party["thread"]: party["memory"]
                    for party in parties
                    if party["thread"] in pair and party["memory"].get("failed_gate")
                }
                if memories:
                    clauses.append({
                        "clause": "failure_memory",
                        "terms": "negotiation inherits prior gate failures as explicit retry constraints",
                        "consent": all(memories.values()),
                        "memories": memories,
                    })
                consent = all(item["consent"] for item in clauses)
                treaties.append({
                    "treaty_id": canonical_hash([braid["braid_id"], pair])[:16],
                    "protocol": TREATY_PROTOCOL,
                    "braid_id": braid["braid_id"],
                    "parties": [left, right],
                    "clauses": clauses,
                    "status": "ratified" if consent else "rejected",
                    "signature": canonical_hash([clauses, pair])[:24],
                })

    ratified = sum(treaty["status"] == "ratified" for treaty in treaties)
    return {
        "schema": "aleph.constellation.treaties.v1",
        "experiment": "lane-treaties",
        "recovery_hash": recovery["recovery_hash"],
        "summary": {
            "treaties": len(treaties),
            "ratified": ratified,
            "rejected": len(treaties) - ratified,
            "parties": sum(len(treaty["parties"]) for treaty in treaties),
            "clauses": sum(len(treaty["clauses"]) for treaty in treaties),
        },
        "treaties": sorted(treaties, key=lambda item: (item["braid_id"], item["treaty_id"])),
        "treaty_hash": canonical_hash(treaties),
    }


def render_treaties(treaties: dict[str, Any]) -> str:
    lines = [
        "# Constellation Lane Treaties",
        "",
        f"Recovery hash: `{treaties['recovery_hash']}`",
        f"Treaty hash: `{treaties['treaty_hash']}`",
        "",
    ]
    for treaty in treaties["treaties"]:
        party_labels = ", ".join("`{}`".format(party["thread"]) for party in treaty["parties"])
        clause_labels = [
            "  - {}: {} ({})".format(
                clause["clause"].replace("_", " ").title(),
                clause["terms"],
                "consent" if clause["consent"] else "refusal",
            )
            for clause in treaty["clauses"]
        ]
        lines.extend([
            "## Treaty `{}` — {}".format(treaty["treaty_id"], treaty["status"].title()),
            "",
            "- Braid: `{}`".format(treaty["braid_id"]),
            "- Parties: {}".format(party_labels),
            "- Clauses:",
            *clause_labels,
            "- Signature: `{}`".format(treaty["signature"]),
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"
