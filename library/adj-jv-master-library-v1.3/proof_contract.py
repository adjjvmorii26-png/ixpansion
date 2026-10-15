"""Machine-checkable proof contracts for Library Core Canon promotion.

Structural validation is offline. CI-run authenticity must additionally be checked
against the GitHub Actions API by the workflow; a JSON claim alone is not proof.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

PROOF_ID = re.compile(r"^P-[0-9]{4,}$")
SHA256 = re.compile(r"^[a-fA-F0-9]{64}$")
ENTRY_ID = re.compile(r"^[A-Z]-[0-9]{2,}$")
COMMIT = re.compile(r"^[a-fA-F0-9]{40,64}$")
KINDS = {"ci_run", "test_run", "file_digest"}


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_proof_contract(doc: dict[str, Any], repo_root: Path | None = None) -> list[str]:
    errors: list[str] = []
    if doc.get("proof_schema_version") != "1.0.0":
        errors.append("proof_schema_version must be '1.0.0'")
    objects = doc.get("proof_objects")
    if not isinstance(objects, list):
        return errors + ["proof_objects must be a list"]
    entries = {
        entry.get("id"): entry
        for shelf in doc.get("shelves", []) if isinstance(shelf, dict)
        for entry in shelf.get("entries", []) if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    }
    proofs: dict[str, dict[str, Any]] = {}
    for i, proof in enumerate(objects):
        loc = f"proof_objects[{i}]"
        if not isinstance(proof, dict):
            errors.append(f"{loc} must be an object")
            continue
        pid = proof.get("id")
        if not isinstance(pid, str) or not PROOF_ID.fullmatch(pid):
            errors.append(f"{loc} has invalid proof ID")
            continue
        if pid in proofs:
            errors.append(f"duplicate proof ID: {pid}")
        proofs[pid] = proof
        kind = proof.get("kind")
        if kind not in KINDS:
            errors.append(f"{pid} has unsupported proof kind")
        subject, artifact = proof.get("subject"), proof.get("artifact")
        verifier, procedure, result = proof.get("verifier"), proof.get("procedure"), proof.get("result")
        if not isinstance(subject, dict) or not ENTRY_ID.fullmatch(str(subject.get("entry_id", ""))) or not _nonempty(subject.get("claim")):
            errors.append(f"{pid} requires subject.entry_id and subject.claim")
        elif subject["entry_id"] not in entries:
            errors.append(f"{pid} references unknown subject entry {subject['entry_id']}")
        if not isinstance(artifact, dict) or not _nonempty(artifact.get("uri")) or not isinstance(artifact.get("sha256"), str) or not SHA256.fullmatch(artifact.get("sha256", "")):
            errors.append(f"{pid} requires artifact.uri and a SHA-256 digest")
        if not isinstance(verifier, dict) or not _nonempty(verifier.get("name")) or not _nonempty(verifier.get("version")):
            errors.append(f"{pid} requires verifier.name and verifier.version")
        if not isinstance(procedure, dict) or not isinstance(procedure.get("command"), list) or not procedure["command"] or any(not _nonempty(x) for x in procedure["command"]) or not _nonempty(procedure.get("environment")) or procedure.get("reproducible") is not True:
            errors.append(f"{pid} requires a reproducible command and pinned environment description")
        if not isinstance(result, dict) or result.get("status") not in {"passed", "failed"} or not _nonempty(result.get("observed_at")):
            errors.append(f"{pid} requires result.status and result.observed_at")
        if kind == "ci_run":
            run = proof.get("run")
            if not isinstance(run, dict) or type(run.get("run_id")) is not int or run.get("run_id", 0) < 1 or not _nonempty(run.get("run_url")) or not _nonempty(run.get("workflow")) or not isinstance(run.get("commit_sha"), str) or not COMMIT.fullmatch(run.get("commit_sha", "")) or run.get("conclusion") not in {"success", "failure", "cancelled", "skipped", "timed_out", "action_required", "neutral"}:
                errors.append(f"{pid} requires immutable CI run metadata")
            if isinstance(result, dict) and result.get("status") == "passed" and isinstance(run, dict) and run.get("conclusion") != "success":
                errors.append(f"{pid} claims passed but CI conclusion is not success")
        if kind == "test_run" and (not isinstance(procedure, dict) or procedure.get("reproducible") is not True):
            errors.append(f"{pid} test_run must be reproducible")
        if kind == "file_digest" and repo_root is not None and isinstance(artifact, dict):
            uri = artifact.get("uri", "")
            if isinstance(uri, str) and uri.startswith("repo://"):
                relative = uri[len("repo://"):]
                target = (repo_root / relative).resolve()
                root = repo_root.resolve()
                if root not in target.parents or not target.is_file():
                    errors.append(f"{pid} file_digest target is missing or outside repository")
                else:
                    actual = hashlib.sha256(target.read_bytes()).hexdigest()
                    if actual.lower() != str(artifact.get("sha256", "")).lower():
                        errors.append(f"{pid} artifact SHA-256 mismatch for {uri}")

    for entry_id, entry in entries.items():
        if entry.get("evidence") != "verified":
            continue
        lifecycle = entry.get("lifecycle")
        refs = lifecycle.get("proof_refs") if isinstance(lifecycle, dict) else None
        if not isinstance(refs, list) or not refs:
            errors.append(f"{entry_id} cannot be Canon without lifecycle.proof_refs")
            continue
        valid_count = 0
        for ref in refs:
            proof = proofs.get(ref)
            if proof is None:
                errors.append(f"{entry_id} references missing proof object {ref}")
                continue
            subject = proof.get("subject")
            if not isinstance(subject, dict):
                errors.append(f"{entry_id} proof {ref} has malformed subject")
                continue
            if subject.get("entry_id") != entry_id:
                errors.append(f"{entry_id} proof {ref} belongs to a different entry")
                continue
            if proof.get("kind") not in {"ci_run", "test_run"}:
                errors.append(f"{entry_id} proof {ref} is not an executable test/CI proof")
                continue
            result = proof.get("result")
            if not isinstance(result, dict) or result.get("status") != "passed":
                errors.append(f"{entry_id} proof {ref} did not pass")
                continue
            procedure = proof.get("procedure")
            if not isinstance(procedure, dict) or procedure.get("reproducible") is not True:
                errors.append(f"{entry_id} proof {ref} is not reproducible")
                continue
            if proof.get("kind") == "ci_run":
                run = proof.get("run")
                if not isinstance(run, dict) or run.get("conclusion") != "success":
                    errors.append(f"{entry_id} proof {ref} does not point to successful CI")
                    continue
            valid_count += 1
        if valid_count == 0:
            errors.append(f"{entry_id} has no usable machine-checkable Canon proof")
    return errors


def canon_promotion_errors(doc: dict[str, Any], entry_id: str, repo_root: Path | None = None) -> list[str]:
    entries = {
        entry.get("id"): entry
        for shelf in doc.get("shelves", []) if isinstance(shelf, dict)
        for entry in shelf.get("entries", []) if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    }
    entry = entries.get(entry_id)
    if entry is None:
        return [f"unknown entry: {entry_id}"]
    if entry.get("evidence") != "tested":
        return [f"{entry_id} must be tested before Canon promotion (current: {entry.get('evidence')})"]
    lifecycle = entry.get("lifecycle")
    if not isinstance(lifecycle, dict):
        return [f"{entry_id} lifecycle metadata is missing"]
    if not _nonempty(lifecycle.get("version_pin")):
        return [f"{entry_id} requires version_pin before Canon promotion"]
    if not isinstance(lifecycle.get("known_limitations"), list):
        return [f"{entry_id} requires known_limitations"]
    if not isinstance(lifecycle.get("contradiction_watchlist"), list):
        return [f"{entry_id} requires contradiction_watchlist"]
    candidate = dict(doc)
    candidate_entries = []
    for shelf in candidate.get("shelves", []):
        for item in shelf.get("entries", []):
            if item.get("id") == entry_id:
                item["evidence"] = "verified"
                candidate_entries.append(item)
                if isinstance(item.get("lifecycle"), dict):
                    item["lifecycle"]["label"] = "Canon"
    if not isinstance(lifecycle.get("proof_refs"), list) or not lifecycle["proof_refs"]:
        return [f"{entry_id} requires lifecycle.proof_refs before Canon promotion"]
    return validate_proof_contract(candidate, repo_root)
