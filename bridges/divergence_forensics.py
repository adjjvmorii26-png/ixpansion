"""Divergence Forensics — expose mutations hidden by aggregate telemetry.

A dashboard can look calm while an exact simulation state has mutated.  This
module compares semantic state against resonance telemetry, measures that
camouflage effect, and produces a replayable evidence pack for CI and audits.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Any

STATUS_FIELDS = ("chaos", "mood", "mesh_events", "reactor_events", "state_keys")


@dataclass(frozen=True)
class StateDelta:
    """One precise semantic difference between two realities."""

    path: str
    operation: str
    baseline_value: Any
    twin_value: Any

    def payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ForensicDiagnosis:
    """A deterministic interpretation of semantic versus telemetry drift."""

    classification: str
    semantic_changed: bool
    resonance_changed: bool
    semantic_magnitude: float
    resonance_magnitude: float
    camouflage_index: float
    changed_paths: tuple[str, ...]
    changed_status_fields: tuple[str, ...]
    signature_distance: int
    evidence_hash: str
    containment: tuple[dict[str, Any], ...]

    def payload(self) -> dict[str, Any]:
        value = asdict(self)
        value["changed_paths"] = list(self.changed_paths)
        value["changed_status_fields"] = list(self.changed_status_fields)
        value["containment"] = list(self.containment)
        return value


def _leaf_count(value: Any) -> int:
    if isinstance(value, dict):
        return sum(_leaf_count(item) for item in value.values()) or 1
    if isinstance(value, (list, tuple)):
        return sum(_leaf_count(item) for item in value) or 1
    return 1


def diff_state(baseline: Any, twin: Any, *, path: str = "$") -> list[dict[str, Any]]:
    """Return a stable recursive JSON-path diff between two states."""
    if baseline == twin:
        return []
    if isinstance(baseline, dict) and isinstance(twin, dict):
        deltas: list[dict[str, Any]] = []
        for key in sorted(set(baseline) | set(twin)):
            child_path = f"{path}.{key}"
            if key not in baseline:
                deltas.append(StateDelta(child_path, "added", None, twin[key]).payload())
            elif key not in twin:
                deltas.append(StateDelta(child_path, "removed", baseline[key], None).payload())
            else:
                deltas.extend(diff_state(baseline[key], twin[key], path=child_path))
        return deltas

    if isinstance(baseline, (list, tuple)) and isinstance(twin, (list, tuple)):
        deltas = []
        for index in range(max(len(baseline), len(twin))):
            child_path = f"{path}[{index}]"
            if index >= len(baseline):
                deltas.append(StateDelta(child_path, "added", None, twin[index]).payload())
            elif index >= len(twin):
                deltas.append(StateDelta(child_path, "removed", baseline[index], None).payload())
            else:
                deltas.extend(diff_state(baseline[index], twin[index], path=child_path))
        return deltas

    return [StateDelta(path, "changed", baseline, twin).payload()]


def signature_distance(baseline: str, twin: str) -> int:
    """Compute hexadecimal fingerprint distance, tolerating malformed lengths."""
    return sum(a != b for a, b in zip(baseline, twin)) + abs(len(baseline) - len(twin))


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, round(value, 6)))


def _changed_status_fields(
    baseline_status: dict[str, Any], twin_status: dict[str, Any]
) -> tuple[str, ...]:
    return tuple(field for field in STATUS_FIELDS if baseline_status.get(field) != twin_status.get(field))


def quarantine_plan(deltas: list[dict[str, Any]]) -> tuple[dict[str, Any], ...]:
    """Recommend deterministic containment without inventing risk scores."""
    actions: dict[str, str] = {"added": "observe", "changed": "mask_and_verify", "removed": "restore_from_baseline"}
    plan = []
    for delta in sorted(deltas, key=lambda item: item["path"]):
        depth = delta["path"].count(".") + delta["path"].count("[")
        plan.append({
            "path": delta["path"],
            "operation": delta["operation"],
            "action": actions[delta["operation"]],
            "blast_radius": depth,
            "containment": "semantic_isolation",
        })
    return tuple(plan)


def diagnose_divergence(
    *,
    baseline_state: dict[str, Any],
    twin_state: dict[str, Any],
    baseline_status: dict[str, Any],
    twin_status: dict[str, Any],
    baseline_signature: str,
    twin_signature: str,
) -> ForensicDiagnosis:
    """Compare exact semantics with aggregate resonance and classify the split."""
    deltas = diff_state(baseline_state, twin_state)
    status_changed = _changed_status_fields(baseline_status, twin_status)
    semantic_changed = bool(deltas)
    resonance_changed = bool(status_changed or baseline_signature != twin_signature)
    distance = signature_distance(baseline_signature, twin_signature)

    semantic_magnitude = (
        len(deltas) / max(_leaf_count(baseline_state), _leaf_count(twin_state), 1)
        if semantic_changed
        else 0.0
    )
    resonance_magnitude = max(
        distance / 64,
        len(status_changed) / len(STATUS_FIELDS),
    ) if resonance_changed else 0.0

    if semantic_changed and not resonance_changed:
        classification = "latent_mutation"
    elif resonance_changed and not semantic_changed:
        classification = "phantom_signal"
    elif semantic_changed and resonance_changed:
        classification = "visible_mutation"
    else:
        classification = "synchronized"

    camouflage_index = (
        _clamp01(1.0 - resonance_magnitude / semantic_magnitude)
        if semantic_magnitude > 0
        else 0.0
    )

    evidence_inputs = {
        "baseline_signature": baseline_signature,
        "baseline_state": baseline_state,
        "baseline_status": baseline_status,
        "deltas": deltas,
        "resonance_magnitude": resonance_magnitude,
        "semantic_magnitude": semantic_magnitude,
        "twin_signature": twin_signature,
        "twin_state": twin_state,
        "twin_status": twin_status,
    }
    canonical = json.dumps(
        evidence_inputs, sort_keys=True, separators=(",", ":"), default=str
    )
    evidence_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    return ForensicDiagnosis(
        classification=classification,
        semantic_changed=semantic_changed,
        resonance_changed=resonance_changed,
        semantic_magnitude=_clamp01(semantic_magnitude),
        resonance_magnitude=_clamp01(resonance_magnitude),
        camouflage_index=camouflage_index,
        changed_paths=tuple(delta["path"] for delta in deltas),
        changed_status_fields=status_changed,
        signature_distance=distance,
        evidence_hash=evidence_hash,
        containment=quarantine_plan(deltas),
    )


def diagnosis_from_twin_outcome(outcome: dict[str, Any]) -> ForensicDiagnosis:
    """Re-run forensics from a persisted Counterfactual Twin timeline record."""
    baseline_pulse = outcome["baseline"]
    twin_pulse = outcome["twin"]
    return diagnose_divergence(
        baseline_state=outcome.get("baseline_state", {}),
        twin_state=outcome.get("twin_state", {}),
        baseline_status={field: baseline_pulse[field] for field in STATUS_FIELDS},
        twin_status={field: twin_pulse[field] for field in STATUS_FIELDS},
        baseline_signature=baseline_pulse["signature"],
        twin_signature=twin_pulse["signature"],
    )
