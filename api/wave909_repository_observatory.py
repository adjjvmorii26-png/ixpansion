"""Wave 909 — SkillForge Repository Observatory.

A deterministic, descriptive repository-analysis layer inspired by SKILLFORGE.
It inventories a supplied repository manifest and exposes evidence gaps without
ranking modules or claiming semantic correctness.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List


def _fingerprint(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _category(path: str) -> str:
    if path.startswith("tests/") or "/tests/" in path:
        return "tests"
    if path.startswith("docs/") or path.endswith(".md"):
        return "docs"
    if path.startswith("api/"):
        return "api"
    if path.startswith(".github/"):
        return "automation"
    return "other"


def build(files: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    files = files or []
    normalized = []
    for item in files:
        path = str(item.get("path", ""))
        if not path:
            continue
        normalized.append(
            {
                "path": path,
                "size": int(item.get("size", 0) or 0),
                "category": _category(path),
            }
        )

    normalized.sort(key=lambda x: x["path"])

    categories: Dict[str, int] = {}
    for item in normalized:
        categories[item["category"]] = categories.get(item["category"], 0) + 1

    api_modules = {
        item["path"][4:-3]
        for item in normalized
        if item["path"].startswith("api/") and item["path"].endswith(".py")
    }
    test_modules = {
        item["path"][6:-3].removeprefix("test_")
        for item in normalized
        if item["path"].startswith("tests/") and item["path"].endswith(".py")
    }

    unpaired_api = sorted(api_modules - test_modules)

    oversized = sorted(
        (
            {"path": x["path"], "size": x["size"]}
            for x in normalized
            if x["size"] >= 10000
        ),
        key=lambda x: (-x["size"], x["path"]),
    )

    signals = {
        "api_module_count": len(api_modules),
        "test_file_count": categories.get("tests", 0),
        "doc_file_count": categories.get("docs", 0),
        "unpaired_api_module_count": len(unpaired_api),
        "oversized_file_count": len(oversized),
    }

    blindspots = []
    if unpaired_api:
        blindspots.append(
            {
                "kind": "test_surface_gap",
                "paths": [f"api/{name}.py" for name in unpaired_api],
                "evidence": "filename pairing only",
                "status": "candidate",
            }
        )
    if not categories.get("docs"):
        blindspots.append(
            {
                "kind": "documentation_surface_gap",
                "evidence": "manifest contains no docs",
                "status": "candidate",
            }
        )

    evidence_policy = {
        "claims_are_descriptive": True,
        "semantic_correctness_inferred": False,
        "filename_pairing_is_heuristic": True,
        "missing_test_file_is_not_proof_of_missing_tests": True,
    }

    fingerprint = _fingerprint(
        {
            "files": normalized,
            "signals": signals,
            "blindspots": blindspots,
            "evidence_policy": evidence_policy,
        }
    )

    return {
        "wave": 909,
        "name": "skillforge_repository_observatory",
        "file_count": len(normalized),
        "categories": dict(sorted(categories.items())),
        "signals": signals,
        "blindspots": blindspots,
        "oversized_files": oversized,
        "evidence_policy": evidence_policy,
        "repository_fingerprint": fingerprint,
        "replayable": True,
    }


def handler(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    action = payload.get("action", "status")
    if action == "build":
        return build(payload.get("files", []))
    if action == "status":
        return {
            "status": "experimental",
            "wave": 909,
            "name": "skillforge_repository_observatory",
            "purpose": "descriptive repository evidence and blindspot mapping",
        }
    return {"error": "unknown action", "available": ["status", "build"]}


def coherence_vitals() -> dict:
    return {
        "layer": "experimental",
        "status": "active",
        "wave": "909",
        "module": "skillforge_repository_observatory",
    }


def resonates_with() -> list:
    return [
        "wave908_topology_integrity",
        "wave906_evolution_map",
        "skillforge_observatory",
    ]
