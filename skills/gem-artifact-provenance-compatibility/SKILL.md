---
name: gem-artifact-provenance-compatibility
description: Use when packaging, importing, revising, or validating a portable Gem, skill bundle, or plugin export against its canonical seed, source revision, manifest, and target runtime.
---

# Gem Artifact Provenance & Compatibility

## Mission
Ensure every portable artifact can be traced to an authoritative seed and exact source revision, and that its target compatibility is tested rather than assumed. This skill validates packages; it does not activate a Gem in an external account or publish a plugin.

## Authority model
- Notion: canonical skill intent, policy, and seed identity.
- GitHub: executable skill source, tests, CI, and reviewed revisions.
- Gem/plugin archive: derived package with its own version and digest.
- Drive/Dropbox: evidence and archive copies, not competing code authorities.

## Required inputs
`artifact_id`, `artifact_type`, canonical seed page ID, source repository/ref/SHA when applicable, package/plugin ID and release ID when applicable, target runtime/client, declared dependencies, privacy scope, and rollback reference. Missing values remain `UNSET`.

## Procedure
1. Fetch the canonical seed and confirm its identity, current content, and enabled state when relevant.
2. Read the exact GitHub source revision and compare its instruction content with the seed. Normalize only formatting differences; do not normalize away behavior or safety constraints.
3. Inspect package manifests and enumerate every included skill, reference, dependency, permission, and entry point.
4. Reject duplicate names, unresolved relative links, undeclared dependencies, missing manifests, unsafe file paths, secret-like content, and unexplained source drift.
5. Compute source and package digests using available tooling. Record the algorithm and exact bytes hashed; never invent a digest.
6. Build a compatibility matrix for target runtime, plugin manifest version, skill frontmatter, tool dependencies, and known unsupported capabilities.
7. Run static package checks, synthetic desk tests, and target-runtime tests separately. A local parse or archive inspection is not a runtime test.
8. Record the exact release ID and package digest. Read the published release back and compare file inventory and content when the platform supports it.
9. Classify each edge as `MATCHED`, `MISMATCHED`, `MISSING`, or `UNVERIFIED`. Any missing or mismatched critical edge blocks promotion.
10. Produce a promotion packet and stop at `CANDIDATE`. External import, activation, sharing, publication, or production use requires a separate explicit authorization.

## Required evidence
- Canonical Notion page ID and read timestamp.
- GitHub repository, ref, and exact commit SHA.
- Package/plugin ID, version, and release ID.
- File inventory and source-to-export comparison.
- Compatibility matrix and executed test results.
- Artifact digest and rollback reference, where available.

## Failure rules
- Do not treat a successful archive upload as proof of runtime compatibility.
- Do not treat a Gemini Gem seed as an activated Gemini account Gem.
- Do not treat plugin installation as proof that every skill invocation works.
- Do not claim source/export parity from matching filenames alone.
- If source identity or release identity changes during the workflow, restart comparison against the new exact revision.

## Output
Return a lineage graph, compatibility matrix, file-level drift report, exact evidence references, unresolved gaps, and a lifecycle verdict: `PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`. Promotion remains separate.
