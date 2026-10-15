"""Validate the ADJJV Master Library manifest without external dependencies."""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

MANIFEST_PATH = Path(__file__).with_name("manifest.json")
EVIDENCE_CLASSES = {"idea", "hypothesis", "implemented", "tested", "verified"}
ID_PATTERN = re.compile(r"^[A-Z]-[0-9]{2,}$")


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    """Load JSON and require an object at the top level."""
    with path.open(encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError("manifest root must be an object")
    return value


def validate_manifest(doc: dict[str, Any]) -> list[str]:
    """Return deterministic validation errors; an empty list means structurally valid."""
    errors: list[str] = []
    if not isinstance(doc, dict):
        return ["manifest root must be an object"]
    if doc.get("schema_version") != "1.0.0":
        errors.append("schema_version must be '1.0.0'")
    if not isinstance(doc.get("library_version"), str) or not doc["library_version"]:
        errors.append("library_version must be a non-empty string")
    classes = doc.get("evidence_classes")
    if not isinstance(classes, list) or any(not isinstance(item, str) for item in classes) or set(classes) != EVIDENCE_CLASSES:
        errors.append("evidence_classes must contain exactly the supported classes")

    shelves = doc.get("shelves")
    if not isinstance(shelves, list):
        return errors + ["shelves must be a list"]

    ids: dict[str, dict[str, Any]] = {}
    title_to_ids: dict[str, list[str]] = defaultdict(list)
    entries: list[dict[str, Any]] = []
    shelf_ids: set[str] = set()
    for shelf_index, shelf in enumerate(shelves):
        if not isinstance(shelf, dict):
            errors.append(f"shelf[{shelf_index}] must be an object")
            continue
        shelf_id = shelf.get("id")
        if not isinstance(shelf_id, str) or not re.fullmatch(r"[A-Z]", shelf_id):
            errors.append(f"shelf[{shelf_index}] has invalid id")
        elif shelf_id in shelf_ids:
            errors.append(f"duplicate shelf id: {shelf_id}")
        else:
            shelf_ids.add(shelf_id)
        shelf_entries = shelf.get("entries")
        if not isinstance(shelf_entries, list):
            errors.append(f"shelf {shelf_id!r} entries must be a list")
            continue
        for entry_index, entry in enumerate(shelf_entries):
            location = f"shelf {shelf_id!r} entry[{entry_index}]"
            if not isinstance(entry, dict):
                errors.append(f"{location} must be an object")
                continue
            entries.append(entry)
            entry_id = entry.get("id")
            if not isinstance(entry_id, str) or not ID_PATTERN.fullmatch(entry_id):
                errors.append(f"{location} has invalid id")
                continue
            if entry_id in ids:
                errors.append(f"duplicate entry id: {entry_id}")
            else:
                ids[entry_id] = entry
            if entry_id.split("-", 1)[0] != shelf_id:
                errors.append(f"{entry_id} prefix does not match shelf {shelf_id}")
            title = entry.get("title")
            if not isinstance(title, str) or not title.strip():
                errors.append(f"{entry_id} title must be non-empty")
            else:
                title_to_ids[" ".join(title.casefold().split())].append(entry_id)
            if entry.get("evidence") not in EVIDENCE_CLASSES:
                errors.append(f"{entry_id} has unsupported evidence class")
            version = entry.get("version")
            if type(version) is not int or version < 1:
                errors.append(f"{entry_id} version must be a positive integer")
            history = entry.get("history")
            if not isinstance(history, list) or not history:
                errors.append(f"{entry_id} history must be a non-empty list")
            else:
                history_versions = [item.get("version") for item in history if isinstance(item, dict)]
                if (len(history_versions) != len(history) or any(type(v) is not int or v < 1 for v in history_versions) or history_versions != sorted(set(history_versions))):
                    errors.append(f"{entry_id} history versions must be strictly increasing")
                if history_versions and history_versions[-1] != version:
                    errors.append(f"{entry_id} current version must match latest history version")
                for item in history:
                    if not isinstance(item, dict) or not isinstance(item.get("change"), str) or not item["change"].strip() or not isinstance(item.get("reason"), str) or not item["reason"].strip():
                        errors.append(f"{entry_id} history records require non-empty change and reason")
                        break
            for field in ("relations", "contradicts"):
                if not isinstance(entry.get(field), list) or any(not isinstance(ref, str) for ref in entry.get(field, [])):
                    errors.append(f"{entry_id} {field} must be a list of entry IDs")

    for entry_id, entry in ids.items():
        for field in ("relations", "contradicts"):
            refs = entry.get(field)
            if not isinstance(refs, list):
                continue
            for ref in refs:
                if not isinstance(ref, str) or ref not in ids:
                    errors.append(f"{entry_id} has dangling {field} reference: {ref}")
        relations = entry.get("relations")
        contradictions = entry.get("contradicts")
        if isinstance(relations, list) and entry_id in relations:
            errors.append(f"{entry_id} cannot relate to itself")
        if isinstance(contradictions, list) and entry_id in contradictions:
            errors.append(f"{entry_id} cannot contradict itself")

    for normalized_title, matches in sorted(title_to_ids.items()):
        if len(matches) > 1:
            errors.append("possible duplicate titles require review: " + ", ".join(sorted(matches)))
    # Contradictions are not necessarily invalid: they are explicitly surfaced for human review.
    return errors


def find_contradictions(doc: dict[str, Any]) -> list[dict[str, str]]:
    """Return declared contradiction edges once, in stable order."""
    by_id = {
        entry.get("id"): entry
        for shelf in doc.get("shelves", [])
        if isinstance(shelf, dict)
        for entry in shelf.get("entries", [])
        if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    }
    conflicts: set[tuple[str, str]] = set()
    for entry_id, entry in by_id.items():
        for other_id in entry.get("contradicts", []):
            if other_id in by_id and other_id != entry_id:
                conflicts.add(tuple(sorted((entry_id, other_id))))
    return [
        {"left": left, "right": right, "left_title": by_id[left].get("title", ""),
         "right_title": by_id[right].get("title", "")}
        for left, right in sorted(conflicts)
    ]


def build_index(doc: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Build a stable ID index for lookup after validation."""
    index: dict[str, dict[str, Any]] = {}
    for shelf in doc.get("shelves", []):
        for entry in shelf.get("entries", []):
            if isinstance(entry, dict) and isinstance(entry.get("id"), str):
                index[entry["id"]] = entry
    return index


def main() -> int:
    doc = load_manifest()
    errors = validate_manifest(doc)
    report = {
        "library": doc.get("library"),
        "library_version": doc.get("library_version"),
        "entries": sum(len(s.get("entries", [])) for s in doc.get("shelves", []) if isinstance(s, dict)),
        "shelves": len(doc.get("shelves", [])),
        "declared_contradictions": find_contradictions(doc),
        "valid": not errors,
        "errors": errors,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
