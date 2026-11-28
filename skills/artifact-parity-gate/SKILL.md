---
name: artifact-parity-gate
description: Verify canonical artifacts and their GitHub, Google Drive, Notion, or Plugin Creator copies without silently overwriting drift.
---

# Artifact Parity Gate

## Mission
Prove whether copies of one artifact agree across systems. This is a readback protocol, not a sync engine or permission to overwrite, publish, enable, merge, or deploy.

## Required identity
Record canonical source ID/URL, artifact ID, semantic version, parent revision, immutable source commit/ref, expected file inventory, destination IDs/release IDs, readback evidence, timestamp, and verifier. Missing source identity or version is INCOMPLETE.

## Procedure
1. Fetch the saved canonical source; never hash an unsaved draft buffer as canonical.
2. Build a manifest with relative path, media type, byte size, source revision, and SHA-256 when raw bytes are available.
3. For text-only APIs, compute a clearly labeled normalized-text digest. Never call it a byte hash.
4. Record canonicalization algorithm/version. JSON key sorting and UTF-8/line-ending normalization are allowed only when declared. Never normalize away meaningful whitespace, code, permissions, URLs, IDs, or semantic versions.
5. Read every destination back. Confirm exact object IDs and release IDs. Metadata-only readback proves existence/placement, not content parity.
6. Compare inventory, identity, content, and cross-manifest references independently.
7. Classify each result MATCH, DRIFTED, MISSING, INCOMPLETE, BLOCKED, or UNVERIFIABLE. Missing evidence is never a pass.
8. Quarantine drift and preserve both snapshots. Never overwrite, delete, repair, or promote automatically.
9. Propose the smallest repair with canonical source, mismatching paths/fields, copy direction, rollback ref, and required approval. Prefer a new candidate revision.
10. After approval, write the candidate, read it back, and recompute the same digests. Upload success without readback remains UNVERIFIABLE.

## Platform cautions
- Notion: metadata and page text are separate evidence. Fetch saved content and compare a declared text representation.
- GitHub: pin repository, branch, and immutable commit SHA. A branch name alone is mutable.
- Google Drive: metadata confirms identity and placement. Download bytes for SHA-256. Native Docs/Sheets require an explicit export format or normalized text representation.
- Plugin Creator: pin plugin ID and release ID; inspect package inventory and file contents. Release success alone is not parity.
- Archives: hash archive bytes separately from extracted file manifests.

## Evidence levels
- BYTE: SHA-256 from exact raw bytes.
- NORMALIZED_TEXT: digest from a declared canonical text representation.
- METADATA_ONLY: identity and placement only; content parity is UNVERIFIABLE.

## Verdicts
MATCH, DRIFTED, MISSING, INCOMPLETE, BLOCKED, or UNVERIFIABLE.

## Safety
No credentials in manifests/logs, production writes, automatic repair, sync, sharing, skill enablement, plugin release, merge, or deployment. Repairs and promotion require explicit authorization and a separate candidate revision.

## Output
Return pinned source/destination IDs, artifact/version/parent, inventories, hash algorithm and normalization rules, per-file comparison, evidence level, verdict, quarantined mismatches, rollback ref, and next approval boundary.
