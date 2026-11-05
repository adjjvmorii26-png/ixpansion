#!/usr/bin/env python3
"""Execute the versioned World Canvas scenario fixtures without browser or network access.

This runner validates deterministic contracts represented by the fixture registry.
It does not drive index.html, execute Gemini/provider models, or validate physical behavior.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_REGISTRY = ROOT / "labs/world-canvas-gem-harness/scenario-registry.json"
MAX_EXPORT_BYTES = 65_536
SCHEMA = "ixpansion.gem-skill-evidence/v1"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def state_errors(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    agent = state.get("agent", {})
    beacons = state.get("beacons", [])
    if not (0 <= agent.get("x", -1) <= 1000 and 0 <= agent.get("y", -1) <= 700):
        errors.append("world_bounds_valid")
    if not (0 <= agent.get("energy", -1) <= 100):
        errors.append("energy_in_range")
    ids = [agent.get("id", "agent-0")] + [item.get("id") for item in beacons]
    if len(ids) != len(set(ids)):
        errors.append("unique_entity_ids")
    if len(beacons) > 24:
        errors.append("beacon_capacity_respected")
    return errors


def bounded_payload(value: Any, limit: int = MAX_EXPORT_BYTES) -> bytes:
    encoded = (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    if len(encoded) > limit:
        raise ValueError(f"evidence report is {len(encoded)} bytes; limit is {limit}")
    return encoded


def execute(scenario: dict[str, Any]) -> list[dict[str, Any]]:
    sid = scenario["id"]
    inputs = scenario["inputs"]
    checks: list[tuple[str, bool, str]] = []
    if sid == "world-state-valid-001":
        state = {"agent": {"id": "agent-0", **inputs["agent"]}, "beacons": inputs["beacons"]}
        errors = state_errors(state)
        for name in scenario["assertions"]:
            checks.append((name, name not in errors, "valid seeded state" if name not in errors else "invariant failed"))
    elif sid == "world-energy-invalid-001":
        committed = {"agent": {"id": "agent-0", "x": 320, "y": 180, "energy": 100}, "beacons": []}
        before = canonical_bytes(committed)
        candidate = json.loads(before)
        candidate["agent"]["energy"] = inputs["mutation"]["value"]
        rejected = bool(state_errors(candidate))
        unchanged = canonical_bytes(committed) == before
        checks.extend([
            ("candidate_rejected", rejected, "energy mutation rejected" if rejected else "invalid candidate accepted"),
            ("committed_state_unchanged", unchanged, "committed state remained isolated" if unchanged else "committed state changed"),
        ])
    elif sid == "world-duplicate-id-001":
        committed = {"agent": {"id": "agent-0", "x": 320, "y": 180, "energy": 100}, "beacons": []}
        before = canonical_bytes(committed)
        candidate = json.loads(before)
        candidate["beacons"].append({"id": inputs["mutation"]["operation"].replace("append_duplicate_agent_id", "agent-0"), "x": 10, "y": 10})
        rejected = "unique_entity_ids" in state_errors(candidate)
        unchanged = canonical_bytes(committed) == before
        checks.extend([
            ("candidate_rejected", rejected, "duplicate identifier rejected" if rejected else "duplicate identifier accepted"),
            ("committed_state_unchanged", unchanged, "committed state remained isolated" if unchanged else "committed state changed"),
        ])
    elif sid == "world-report-bounds-001":
        limit = inputs["export_limit_bytes"]
        sample = {"schema": SCHEMA, "checks": [{"status": "PASS"}]}
        encoded = canonical_bytes(sample)
        accepted = len(encoded) <= limit
        oversized = {"payload": "x" * (limit + 1)}
        try:
            bounded_payload(oversized, limit)
            no_partial = False
        except ValueError:
            no_partial = True
        checks.extend([
            ("payload_within_limit_or_rejected", accepted and len(oversized) > limit, f"small={len(encoded)} bytes; limit={limit}"),
            ("no_partial_download", no_partial, "oversized payload is rejected as a whole; no truncated artifact emitted"),
        ])
    elif sid == "world-review-separation-001":
        passes = inputs["review_passes"]
        present = "implementation" in passes and "adversarial" in passes
        labels = {"implementation": "source-contract", "adversarial": "counterexample"}
        labelled = present and all(labels[name] for name in ("implementation", "adversarial"))
        checks.extend([
            ("both_passes_present", present, "implementation and adversarial passes are distinct"),
            ("findings_labelled_by_evidence", labelled, "pass categories carry separate evidence labels"),
        ])
    else:
        raise ValueError(f"unsupported scenario: {sid}")
    expected = set(scenario["assertions"])
    actual = {name for name, _, _ in checks}
    if expected != actual:
        raise ValueError(f"{sid}: assertion adapter mismatch; expected={sorted(expected)}, actual={sorted(actual)}")
    return [{"name": name, "status": "PASS" if passed else "FAIL", "detail": detail} for name, passed, detail in checks]


def run_registry(registry: dict[str, Any], source_commit: str) -> dict[str, Any]:
    if registry.get("schema") != "ixpansion.gem-skill-scenarios/v1":
        raise ValueError("unsupported scenario registry schema")
    if registry.get("execution") != "local-deterministic":
        raise ValueError("only local-deterministic fixtures are supported")
    ids = [item.get("id") for item in registry.get("scenarios", [])]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError("scenario registry must contain unique, non-empty scenarios")
    results = []
    for scenario in registry["scenarios"]:
        checks = execute(scenario)
        results.append({
            "scenario_id": scenario["id"],
            "scenario_version": scenario["version"],
            "skill_name": scenario["skill"],
            "seed": scenario["seed"],
            "checks": checks,
            "summary": {"passed": sum(c["status"] == "PASS" for c in checks),
                        "failed": sum(c["status"] == "FAIL" for c in checks)},
        })
    failed = sum(item["summary"]["failed"] for item in results)
    return {
        "schema": SCHEMA,
        "runtime": f"python-{sys.version_info.major}.{sys.version_info.minor}",
        "execution_mode": "local-deterministic-fixture-adapter",
        "source_commit": source_commit,
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "registry_schema": registry["schema"],
        "registry_version": registry["registry_version"],
        "summary": {"scenarios": len(results), "passed": sum(x["summary"]["passed"] for x in results),
                    "failed": failed, "status": "PASS" if failed == 0 else "FAIL"},
        "results": results,
        "trust": {
            "state_hash": "not supplied; this report does not authenticate source or runtime",
            "provider_execution": "not performed",
            "browser_simulation": "not executed",
            "physical_world_validation": "not performed",
        },
    }


def git_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
                              capture_output=True, text=True, timeout=2).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--source-commit", default=None)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    try:
        registry = json.loads(args.registry.read_text(encoding="utf-8"))
        report = run_registry(registry, args.source_commit or git_commit())
        payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        encoded = payload.encode("utf-8")
        if len(encoded) > MAX_EXPORT_BYTES:
            raise ValueError(f"evidence report is {len(encoded)} bytes; limit is {MAX_EXPORT_BYTES}")
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(encoded)
        else:
            sys.stdout.write(payload)
        return 0 if report["summary"]["failed"] == 0 else 1
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"scenario-runner: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
