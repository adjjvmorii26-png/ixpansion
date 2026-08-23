"""Concordance Engine — negotiate treaties between divergent realities.

Counterfactual repair is not always desirable: some differences should win,
some should merge, and some must remain visible as conflicts.  The engine turns
every recursive semantic delta into a treaty clause and produces a deterministic
merged state plus a replayable contract hash.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from bridges.divergence_forensics import diff_state
from bridges.resonance_loom import _atomic_write

RESOLUTIONS = {
    "baseline", "twin", "lexical_min", "lexical_max",
    "union", "preserve_conflict",
}


@dataclass(frozen=True)
class TreatyPolicy:
    """Deterministic rules for reconciling divergent semantic paths."""

    default: str = "lexical_min"
    overrides: dict[str, str] = field(default_factory=dict)
    authorities: dict[str, float] = field(default_factory=dict)
    default_authority_baseline: float = 0.0
    default_authority_twin: float = 0.0

    def payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TreatyClause:
    """One negotiated semantic difference."""

    path: str
    operation: str
    baseline_value: Any
    twin_value: Any
    resolution: str
    resolved_value: Any
    authority_baseline: float
    authority_twin: float
    rationale: str


def _authority_for(path: str, policy: TreatyPolicy) -> tuple[float, float]:
    if path in policy.authorities:
        return policy.default_authority_baseline, float(policy.authorities[path])
    matching = [
        (prefix, score) for prefix, score in policy.authorities.items()
        if path.startswith(prefix + ".") or path.startswith(prefix + "[")
    ]
    if matching:
        _, score = sorted(matching, key=lambda item: (-len(item[0]), item[0]))[0]
        return policy.default_authority_baseline, float(score)
    return policy.default_authority_baseline, policy.default_authority_twin


def _recursive_union(baseline_value: Any, twin_value: Any) -> Any:
    """Merge objects recursively and append unseen list items."""
    if isinstance(baseline_value, dict) and isinstance(twin_value, dict):
        merged = copy.deepcopy(baseline_value)
        for key, twin_child in twin_value.items():
            if key not in merged:
                merged[key] = copy.deepcopy(twin_child)
            elif merged[key] != twin_child:
                merged[key] = _recursive_union(merged[key], twin_child)
        return merged
    if isinstance(baseline_value, list) and isinstance(twin_value, list):
        merged = copy.deepcopy(baseline_value)
        for item in twin_value:
            if item not in merged:
                merged.append(copy.deepcopy(item))
        return merged
    return {"$concordance": {
        "baseline": copy.deepcopy(baseline_value),
        "twin": copy.deepcopy(twin_value),
    }}


def _resolve_clause(
    delta: dict[str, Any], policy: TreatyPolicy
) -> TreatyClause:
    path = delta["path"]
    baseline_value = delta["baseline_value"]
    twin_value = delta["twin_value"]
    override = policy.overrides.get(path)

    if override:
        resolution = override
        rationale = "explicit path override"
    else:
        authority_baseline, authority_twin = _authority_for(path, policy)
        if authority_baseline != authority_twin:
            resolution = "baseline" if authority_baseline > authority_twin else "twin"
            rationale = (
                f"path authority baseline={authority_baseline} twin={authority_twin}"
            )
        else:
            resolution = policy.default
            rationale = "default treaty policy"

    if resolution not in RESOLUTIONS:
        raise ValueError(f"unknown treaty resolution '{resolution}' for {path}")

    if resolution == "baseline":
        value: Any = copy.deepcopy(baseline_value)
    elif resolution == "twin":
        value = copy.deepcopy(twin_value)
    elif resolution in {"lexical_min", "lexical_max"}:
        values = [baseline_value, twin_value]
        try:
            value = copy.deepcopy(min(values) if resolution == "lexical_min" else max(values))
        except TypeError as error:
            raise ValueError(
                f"{resolution} requires comparable values at {path}"
            ) from error
    elif resolution == "union":
        value = _recursive_union(baseline_value, twin_value)
        rationale += "; deterministic recursive union"
    else:
        value = {"$conflict": {
            "baseline": copy.deepcopy(baseline_value),
            "twin": copy.deepcopy(twin_value),
        }}
        rationale += "; conflict intentionally preserved"

    return TreatyClause(
        path=path,
        operation=delta["operation"],
        baseline_value=copy.deepcopy(baseline_value),
        twin_value=copy.deepcopy(twin_value),
        resolution=resolution,
        resolved_value=value,
        authority_baseline=policy.default_authority_baseline,
        authority_twin=policy.default_authority_twin,
        rationale=rationale,
    )


def _segments(path: str) -> list[tuple[str, Any]]:
    if not path.startswith("$"):
        raise ValueError(f"semantic paths must begin with '$': {path}")
    segments: list[tuple[str, Any]] = []
    token = ""
    index = 1
    while index < len(path):
        char = path[index]
        if char == ".":
            if token:
                segments.append(("key", token))
            token = ""
        elif char == "[":
            if token:
                segments.append(("key", token))
                token = ""
            end = path.index("]", index)
            segments.append(("index", int(path[index + 1:end])))
            index = end
        else:
            token += char
        index += 1
    if token:
        segments.append(("key", token))
    return segments


def _apply_resolved_value(state: Any, path: str, operation: str, value: Any) -> Any:
    segments = _segments(path)
    if not segments:
        return value
    cursor = state
    for kind, key in segments[:-1]:
        if kind == "key":
            cursor = cursor.setdefault(key, {})
        else:
            while len(cursor) <= key:
                cursor.append({})
            cursor = cursor[key]
    kind, key = segments[-1]
    if operation == "removed":
        if isinstance(cursor, dict):
            cursor.pop(key, None)
        elif isinstance(cursor, list) and isinstance(key, int) and 0 <= key < len(cursor):
            cursor.pop(key)
        return state
    if kind == "key":
        if not isinstance(cursor, dict):
            raise ValueError(f"cannot apply key path {path} to non-object")
        cursor[key] = value
    else:
        if not isinstance(cursor, list):
            raise ValueError(f"cannot apply index path {path} to non-array")
        while len(cursor) <= key:
            cursor.append(None)
        cursor[key] = value
    return state


def _get_path_value(state: Any, path: str) -> Any:
    cursor = state
    for kind, key in _segments(path):
        try:
            cursor = cursor[key]
        except (KeyError, IndexError, TypeError):
            raise ValueError(f"path does not exist: {path}") from None
    return cursor


def _union_ancestor(path: str, baseline_state: Any, twin_state: Any) -> str | None:
    segments = _segments(path)
    candidates = []
    for end in range(1, len(segments)):
        parts = segments[:end]
        rebuilt = "$"
        for kind, key in parts:
            rebuilt += f"[{key}]" if kind == "index" else f".{key}"
        try:
            baseline_value = _get_path_value(baseline_state, rebuilt)
            twin_value = _get_path_value(twin_state, rebuilt)
        except ValueError:
            continue
        if (
            isinstance(baseline_value, (dict, list))
            and isinstance(twin_value, (dict, list))
        ):
            candidates.append(rebuilt)
    return candidates[-1] if candidates else None


def _coalesce_collection_deltas(
    deltas: list[dict[str, Any]],
    baseline_state: dict[str, Any],
    twin_state: dict[str, Any],
    policy: TreatyPolicy,
) -> list[dict[str, Any]]:
    """Represent collection-wide unions as one clause rather than leaf noise."""
    covered: set[str] = set()
    synthesized: list[dict[str, Any]] = []
    for delta in deltas:
        path = delta["path"]
        if path in covered or path in policy.overrides:
            continue
        ancestor = _union_ancestor(path, baseline_state, twin_state)
        if not ancestor or ancestor in policy.overrides:
            continue
        if ancestor in covered:
            continue
        try:
            baseline_value = copy.deepcopy(_get_path_value(baseline_state, ancestor))
            twin_value = copy.deepcopy(_get_path_value(twin_state, ancestor))
        except ValueError:
            continue
        covered.update(
            item["path"] for item in deltas if item["path"].startswith(ancestor + ".")
        )
        covered.update(
            item["path"] for item in deltas if item["path"].startswith(ancestor + "[")
        )
        synthesized.append({
            "path": ancestor,
            "operation": "changed",
            "baseline_value": baseline_value,
            "twin_value": twin_value,
        })
    surviving = [item for item in deltas if item["path"] not in covered]
    return sorted(surviving + synthesized, key=lambda item: item["path"])


def negotiate_treaty(
    baseline_state: dict[str, Any],
    twin_state: dict[str, Any],
    policy: TreatyPolicy | None = None,
) -> dict[str, Any]:
    """Negotiate every recursive difference into a deterministic merged state."""
    policy = policy or TreatyPolicy()
    deltas = diff_state(baseline_state, twin_state)
    if policy.default == "union":
        deltas = _coalesce_collection_deltas(deltas, baseline_state, twin_state, policy)
    clauses = [
        _resolve_clause(delta, policy)
        for delta in deltas
    ]
    merged_state = copy.deepcopy(baseline_state)
    # Apply removals last-in-first-out so captured list indices stay stable.
    ordered_clauses = sorted(
        clauses,
        key=lambda clause: (clause.operation == "removed", clause.path),
        reverse=True,
    )
    for clause in ordered_clauses:
        merged_state = _apply_resolved_value(
            merged_state, clause.path, clause.operation, clause.resolved_value
        )

    preserved_conflicts = sum(
        clause.resolution == "preserve_conflict" for clause in clauses
    )
    matches_baseline = merged_state == baseline_state
    matches_twin = merged_state == twin_state
    payload = {
        "experiment": "concordance-treaty",
        "engine_version": 1,
        "policy": policy.payload(),
        "clause_count": len(clauses),
        "preserved_conflicts": preserved_conflicts,
        "clauses": [asdict(clause) for clause in clauses],
        "merged_state": merged_state,
        "matches_baseline": matches_baseline,
        "matches_twin": matches_twin,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    payload["treaty_hash"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    payload["ratified"] = all(
        clause["resolution"] in RESOLUTIONS for clause in payload["clauses"]
    )
    return payload


def load_state_spec(path: Path) -> dict[str, Any]:
    spec = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(spec.get("baseline_state"), dict) or not isinstance(spec.get("twin_state"), dict):
        raise ValueError("state specification requires baseline_state and twin_state objects")
    raw_policy = spec.get("policy", {})
    policy = TreatyPolicy(
        default=raw_policy.get("default", "lexical_min"),
        overrides=dict(raw_policy.get("overrides", {})),
        authorities={key: float(value) for key, value in raw_policy.get("authorities", {}).items()},
        default_authority_baseline=float(raw_policy.get("default_authority_baseline", 0.0)),
        default_authority_twin=float(raw_policy.get("default_authority_twin", 0.0)),
    )
    if policy.default not in RESOLUTIONS or any(value not in RESOLUTIONS for value in policy.overrides.values()):
        raise ValueError("policy contains an unknown resolution")
    return {"baseline_state": spec["baseline_state"], "twin_state": spec["twin_state"], "policy": policy}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Negotiate divergent-state treaties")
    commands = parser.add_subparsers(dest="command", required=True)
    forge = commands.add_parser("forge", help="forge a concordance treaty")
    forge.add_argument("--spec", type=Path, required=True)
    forge.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        spec = load_state_spec(args.spec)
        report = negotiate_treaty(spec["baseline_state"], spec["twin_state"], spec["policy"])
        args.output.parent.mkdir(parents=True, exist_ok=True)
        rendered = json.dumps(report, sort_keys=True, indent=2) + "\n"
        _atomic_write(args.output, rendered)
        print(json.dumps({
            "output": str(args.output),
            "treaty_hash": report["treaty_hash"],
            "ratified": report["ratified"],
            "clauses": report["clause_count"],
            "preserved_conflicts": report["preserved_conflicts"],
        }, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError, TypeError) as error:
        print(json.dumps({"error": str(error)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
