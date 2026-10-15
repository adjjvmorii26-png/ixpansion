"""Archivist of Coherence — Library Core v1.3 Integrity Epoch.

CHARTER
- ID Sanctity: IDs are unique, shelf-prefixed, and reserved forever after retirement.
- Lineage Discipline: evidence moves one state at a time; downgrades require reason and trigger.
- Relationship Honesty: every edge resolves to a real entry with versioned history.
- Contradiction Visibility: conflicts are explicit frontier records, never silently erased.
- No lore without proof: labels describe declared evidence; they do not prove it exists.

This validator is a gate used by CI and contributor workflows. It is not a running service.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any

MANIFEST_PATH = Path(__file__).with_name("manifest.json")
EVIDENCE_ORDER = ("idea", "hypothesis", "implemented", "tested", "verified")
EVIDENCE_CLASSES = set(EVIDENCE_ORDER)
ID_PATTERN = re.compile(r"^[A-Z]-[0-9]{2,}$")
VALID_ACTORS = {"you", "agent", "ci", "user", "maintainer", "system"}
VALID_TRIGGERS = {"contradiction", "bug", "new_data", "design_change", "deprecation"}
CONTRADICTION_TAG = "frontier"
VALID_DIMENSIONS = {"performance", "correctness", "security", "reliability", "philosophy", "scope", "other"}
VALID_RESOLUTIONS = {"needs experiment", "needs design decision", "needs deprecation", "resolved", "accepted tradeoff"}


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError("manifest root must be an object")
    return value


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _all_entries(doc: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    found = []
    for shelf in doc.get("shelves", []) if isinstance(doc.get("shelves"), list) else []:
        if isinstance(shelf, dict) and isinstance(shelf.get("entries"), list):
            for entry in shelf["entries"]:
                if isinstance(entry, dict):
                    found.append((str(shelf.get("id", "?")), entry))
    return found


def validate_manifest(doc: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(doc, dict):
        return ["manifest root must be an object"]
    if doc.get("schema_version") != "1.0.0":
        errors.append("schema_version must be '1.0.0'")
    if doc.get("library") != "Library Core":
        errors.append("library must be 'Library Core'")
    if doc.get("release_name") != "Integrity Epoch":
        errors.append("release_name must be 'Integrity Epoch'")
    if not _nonempty(doc.get("library_version")):
        errors.append("library_version must be a non-empty string")
    if not isinstance(doc.get("governance"), dict) or doc["governance"].get("charter") != "Archivist of Coherence" or doc["governance"].get("law") != "No lore without proof":
        errors.append("governance charter and law are required")
    if doc.get("evidence_classes") != list(EVIDENCE_ORDER):
        errors.append("evidence_classes must exactly match the ordered evidence ladder")

    shelves = doc.get("shelves")
    if not isinstance(shelves, list):
        return errors + ["shelves must be a list"]

    active: dict[str, dict[str, Any]] = {}
    title_to_ids: dict[str, list[str]] = defaultdict(list)
    shelf_ids: set[str] = set()
    for shelf_index, shelf in enumerate(shelves):
        if not isinstance(shelf, dict):
            errors.append(f"shelf[{shelf_index}] must be an object")
            continue
        sid = shelf.get("id")
        if not isinstance(sid, str) or not re.fullmatch(r"[A-Z]", sid):
            errors.append(f"shelf[{shelf_index}] has invalid id")
        elif sid in shelf_ids:
            errors.append(f"duplicate shelf id: {sid}")
        else:
            shelf_ids.add(sid)
        entries = shelf.get("entries")
        if not isinstance(entries, list):
            errors.append(f"shelf {sid!r} entries must be a list")
            continue
        for n, entry in enumerate(entries):
            loc = f"shelf {sid!r} entry[{n}]"
            if not isinstance(entry, dict):
                errors.append(f"{loc} must be an object")
                continue
            eid = entry.get("id")
            if not isinstance(eid, str) or not ID_PATTERN.fullmatch(eid):
                errors.append(f"{loc} has invalid id")
                continue
            if eid in active:
                errors.append(f"duplicate entry id: {eid}")
            else:
                active[eid] = entry
            if eid.split("-", 1)[0] != sid:
                errors.append(f"{eid} prefix does not match shelf {sid}")
            title = entry.get("title")
            if not _nonempty(title):
                errors.append(f"{eid} title must be non-empty")
            else:
                title_to_ids[" ".join(title.casefold().split())].append(eid)
            if entry.get("evidence") not in EVIDENCE_CLASSES:
                errors.append(f"{eid} has unsupported evidence class")
            if type(entry.get("version")) is not int or entry.get("version", 0) < 1:
                errors.append(f"{eid} version must be a positive integer")
            if not isinstance(entry.get("origin"), dict) or not _nonempty(entry["origin"].get("source")) or not _nonempty(entry["origin"].get("ref")):
                errors.append(f"{eid} requires origin.source and origin.ref")
            history = entry.get("history")
            if not isinstance(history, list) or not history:
                errors.append(f"{eid} history must be a non-empty list")
                history = []
            versions = []
            prior_state = None
            for i, event in enumerate(history):
                if not isinstance(event, dict):
                    errors.append(f"{eid} history[{i}] must be an object")
                    continue
                hv = event.get("version")
                versions.append(hv)
                for field in ("change", "reason", "timestamp", "actor", "evidence_ref"):
                    if not _nonempty(event.get(field)):
                        errors.append(f"{eid} history[{i}] requires non-empty {field}")
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", str(event.get("timestamp", ""))):
                    errors.append(f"{eid} history[{i}] timestamp must be UTC ISO-8601 seconds")
                if event.get("actor") not in VALID_ACTORS:
                    errors.append(f"{eid} history[{i}] actor is not recognized")
                fromstate, tostate = event.get("fromstate"), event.get("tostate")
                if tostate not in EVIDENCE_CLASSES:
                    errors.append(f"{eid} history[{i}] has invalid tostate")
                if i == 0:
                    if fromstate is not None:
                        errors.append(f"{eid} initial history event fromstate must be null")
                else:
                    if fromstate != prior_state:
                        errors.append(f"{eid} history[{i}] fromstate must match prior tostate")
                    if fromstate not in EVIDENCE_CLASSES or tostate not in EVIDENCE_CLASSES:
                        pass
                    else:
                        delta = EVIDENCE_ORDER.index(tostate) - EVIDENCE_ORDER.index(fromstate)
                        if delta > 1:
                            errors.append(f"{eid} history[{i}] skips evidence levels")
                        if delta < 0 and (not _nonempty(event.get("reason")) or event.get("trigger") not in VALID_TRIGGERS):
                            errors.append(f"{eid} downgrade requires reason and recognized trigger")
                        if delta == 0:
                            errors.append(f"{eid} history[{i}] must change evidence state")
                prior_state = tostate
                if i > 0 and type(hv) is int and type(versions[0]) is int and hv <= versions[i-1]:
                    errors.append(f"{eid} history versions must be strictly increasing")
            if versions and type(entry.get("version")) is int and versions[-1] != entry["version"]:
                errors.append(f"{eid} current version must match latest history version")
            if history and isinstance(history[-1], dict) and history[-1].get("tostate") != entry.get("evidence"):
                errors.append(f"{eid} current evidence must match latest history tostate")
            for field in ("relations", "contradicts"):
                refs = entry.get(field)
                if not isinstance(refs, list) or any(not isinstance(ref, str) for ref in refs):
                    errors.append(f"{eid} {field} must be a list of entry IDs")
            if eid in entry.get("relations", []) if isinstance(entry.get("relations"), list) else False:
                errors.append(f"{eid} cannot relate to itself")
            if eid in entry.get("contradicts", []) if isinstance(entry.get("contradicts"), list) else False:
                errors.append(f"{eid} cannot contradict itself")
            _validate_lifecycle(eid, entry, errors)

    # A permanent registry prevents a retired ID from being silently reused.
    registry = doc.get("identity_registry")
    if not isinstance(registry, list):
        errors.append("identity_registry must be a list of active and retired IDs")
        registry = []
    reserved: dict[str, dict[str, Any]] = {}
    for i, record in enumerate(registry):
        if not isinstance(record, dict) or not _nonempty(record.get("id")) or record.get("status") not in {"active", "retired"} or not _nonempty(record.get("first_seen")):
            errors.append(f"identity_registry[{i}] requires id, status, and first_seen")
            continue
        rid = record["id"]
        if rid in reserved:
            errors.append(f"duplicate reserved ID: {rid}")
        reserved[rid] = record
    for eid in active:
        if eid not in reserved:
            errors.append(f"{eid} missing from permanent identity_registry")
        elif reserved[eid].get("status") != "active":
            errors.append(f"{eid} is active but its reserved ID status is retired")
    for rid, record in reserved.items():
        if record.get("status") == "active" and rid not in active:
            errors.append(f"reserved ID {rid} marked active but no active entry exists")
        if record.get("status") == "retired" and rid in active:
            errors.append(f"retired ID {rid} cannot be reused")

    for eid, entry in active.items():
        for field in ("relations", "contradicts"):
            refs = entry.get(field)
            if isinstance(refs, list):
                for ref in refs:
                    if not isinstance(ref, str) or ref not in active:
                        errors.append(f"{eid} has dangling {field} reference: {ref}")
                    elif type(active[ref].get("version")) is not int or active[ref].get("version", 0) < 1 or not isinstance(active[ref].get("history"), list) or not active[ref].get("history"):
                        errors.append(f"{eid} {field} reference {ref} is not versioned")
    errors.extend(_validate_contradiction_atlas(doc, active))
    for _, matches in sorted(title_to_ids.items()):
        if len(matches) > 1:
            errors.append("possible duplicate titles require review: " + ", ".join(sorted(matches)))
    return errors


def _validate_lifecycle(eid: str, entry: dict[str, Any], errors: list[str]) -> None:
    state = entry.get("evidence")
    lifecycle = entry.get("lifecycle")
    labels = {"idea":"Spark", "hypothesis":"Claim", "implemented":"In the wild", "tested":"Trialed", "verified":"Canon"}
    if not isinstance(lifecycle, dict) or lifecycle.get("label") != labels.get(state):
        errors.append(f"{eid} lifecycle label does not match evidence state")
        return
    if state == "hypothesis":
        if not _nonempty(lifecycle.get("expected_impact")) or not _nonempty(lifecycle.get("falsifiable_condition")):
            errors.append(f"{eid} hypothesis requires expected_impact and falsifiable_condition")
        if not isinstance(lifecycle.get("related_entries"), list):
            errors.append(f"{eid} hypothesis requires related_entries")
    elif state == "implemented":
        if not isinstance(lifecycle.get("code_refs"), list) or not lifecycle["code_refs"]:
            errors.append(f"{eid} implemented entry requires code_refs")
        if not isinstance(lifecycle.get("repo_links"), list) or not lifecycle["repo_links"]:
            errors.append(f"{eid} implemented entry requires repo_links")
        if not _nonempty(lifecycle.get("branch")) or type(lifecycle.get("pull_request")) is not int or not _nonempty(lifecycle.get("outcome")):
            errors.append(f"{eid} implemented entry requires branch, pull_request, and outcome")
    elif state == "tested":
        if not isinstance(lifecycle.get("test_refs"), list) or not lifecycle["test_refs"]:
            errors.append(f"{eid} tested entry requires test_refs")
        if not isinstance(lifecycle.get("metrics"), dict) or not isinstance(lifecycle.get("failure_modes"), list):
            errors.append(f"{eid} tested entry requires metrics and failure_modes")
    elif state == "verified":
        if not _nonempty(lifecycle.get("version_pin")) or not isinstance(lifecycle.get("known_limitations"), list) or not isinstance(lifecycle.get("contradiction_watchlist"), list):
            errors.append(f"{eid} canon entry requires version_pin, known_limitations, and contradiction_watchlist")


def _validate_contradiction_atlas(doc: dict[str, Any], active: dict[str, dict[str, Any]]) -> list[str]:
    errors = []
    atlas = doc.get("contradiction_atlas")
    if not isinstance(atlas, list):
        return ["contradiction_atlas must be a list"]
    seen = set()
    atlas_pairs = set()
    for i, item in enumerate(atlas):
        if not isinstance(item, dict):
            errors.append(f"contradiction_atlas[{i}] must be an object")
            continue
        cid = item.get("id")
        pair = item.get("entries")
        if not _nonempty(cid) or cid in seen:
            errors.append(f"contradiction_atlas[{i}] requires unique id")
        seen.add(cid)
        if not isinstance(pair, list) or len(pair) < 2 or any(not isinstance(x, str) or x not in active for x in pair) or len(set(pair)) < 2:
            errors.append(f"contradiction_atlas[{i}] entries must reference at least two distinct active entries")
            continue
        if item.get("tag") != CONTRADICTION_TAG:
            errors.append(f"{cid} contradiction must be tagged frontier")
        if item.get("status") not in {"active", "resolved", "accepted_tradeoff", "deprecated"}:
            errors.append(f"{cid} has invalid contradiction status")
        if item.get("dimension") not in VALID_DIMENSIONS:
            errors.append(f"{cid} has invalid conflict dimension")
        if item.get("resolution_path") not in VALID_RESOLUTIONS:
            errors.append(f"{cid} has invalid resolution_path")
        if not _nonempty(item.get("description")) or not _nonempty(item.get("shelf")):
            errors.append(f"{cid} requires description and shelf")
        if item.get("status") == "resolved" and not _nonempty(item.get("resolution_ref")):
            errors.append(f"{cid} resolved contradiction requires resolution_ref")
        if item.get("status") in {"active", "accepted_tradeoff"} and not _nonempty(item.get("follow_up")):
            errors.append(f"{cid} active/accepted contradiction requires follow_up")
        normalized = tuple(sorted(set(pair)))
        atlas_pairs.add(normalized)
    declared_pairs = set()
    for eid, entry in active.items():
        for other in entry.get("contradicts", []) if isinstance(entry.get("contradicts"), list) else []:
            if isinstance(other, str) and other in active and other != eid:
                declared_pairs.add(tuple(sorted((eid, other))))
    for pair in declared_pairs:
        if not any(set(pair).issubset(set(atlas_pair)) for atlas_pair in atlas_pairs):
            errors.append(f"contradiction {pair[0]} <> {pair[1]} missing from contradiction_atlas")
    for pair in atlas_pairs:
        for eid in pair:
            for other in pair:
                if eid != other and other not in active[eid].get("contradicts", []):
                    errors.append(f"atlas conflict {eid} <> {other} must be declared by both entries")
    return errors


def find_contradictions(doc: dict[str, Any]) -> list[dict[str, Any]]:
    atlas = doc.get("contradiction_atlas", [])
    return sorted((item for item in atlas if isinstance(item, dict)), key=lambda x: str(x.get("id", "")))


def build_index(doc: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {entry["id"]: entry for _, entry in _all_entries(doc) if isinstance(entry.get("id"), str)}


def validate_lineage_delta(base: dict[str, Any], head: dict[str, Any]) -> list[str]:
    """Check state jumps between two manifests, as a CI pull-request gate."""
    errors = []
    old = build_index(base)
    new = build_index(head)
    old_registry = {item.get("id"): item for item in base.get("identity_registry", []) if isinstance(item, dict) and isinstance(item.get("id"), str)}
    new_registry = {item.get("id"): item for item in head.get("identity_registry", []) if isinstance(item, dict) and isinstance(item.get("id"), str)}
    for reserved_id, old_record in old_registry.items():
        if reserved_id not in new_registry:
            errors.append(f"reserved ID {reserved_id} was removed from identity_registry")
        elif old_record.get("status") == "retired" and new_registry[reserved_id].get("status") != "retired":
            errors.append(f"retired ID {reserved_id} cannot be reactivated")
    for eid, after in new.items():
        if eid not in old:
            continue
        before = old[eid]
        a, b = before.get("evidence"), after.get("evidence")
        if a in EVIDENCE_CLASSES and b in EVIDENCE_CLASSES and abs(EVIDENCE_ORDER.index(b)-EVIDENCE_ORDER.index(a)) > 1:
            errors.append(f"{eid} jumps more than one evidence level in one PR: {a} -> {b}")
        old_contradictions = set(before.get("contradicts", []))
        new_contradictions = set(after.get("contradicts", []))
        added = new_contradictions - old_contradictions
        if added:
            for other in sorted(added):
                atlas = [x for x in head.get("contradiction_atlas", []) if isinstance(x, dict) and set(x.get("entries", [])) == {eid, other}]
                if not atlas:
                    errors.append(f"new contradiction {eid} <> {other} requires a contradiction_atlas frontier record")
    return errors


def _load_git_manifest(ref: str, manifest_relative: str) -> dict[str, Any]:
    raw = subprocess.check_output(["git", "show", f"{ref}:{manifest_relative}"], text=True)
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError(f"{ref}:{manifest_relative} is not a JSON object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Library Core manifest and optional PR lineage delta.")
    parser.add_argument("--base-ref", help="Git ref to compare against HEAD for PR lineage sanity")
    parser.add_argument("--manifest", default=str(MANIFEST_PATH), help="Path to manifest JSON")
    args = parser.parse_args()
    path = Path(args.manifest)
    doc = load_manifest(path)
    errors = validate_manifest(doc)
    if args.base_ref:
        try:
            manifest_relative = "library/adj-jv-master-library-v1.3/manifest.json"
            base = _load_git_manifest(args.base_ref, manifest_relative)
            errors.extend(validate_lineage_delta(base, doc))
        except (subprocess.CalledProcessError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"could not validate lineage delta against {args.base_ref}: {exc}")
    report = {
        "library": doc.get("library"),
        "release_name": doc.get("release_name"),
        "library_version": doc.get("library_version"),
        "shelves": len(doc.get("shelves", [])),
        "entries": len(build_index(doc)),
        "active_contradictions": sum(1 for x in find_contradictions(doc) if x.get("status") == "active"),
        "contradiction_atlas": find_contradictions(doc),
        "valid": not errors,
        "errors": errors,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
