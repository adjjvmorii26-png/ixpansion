---
name: seed-surface-reconciler
description: Use when comparing canonical Notion skill seeds with GitHub implementations, Gem exports, plugin packages, and Drive or Dropbox archive copies.
---

# Seed-to-Surface Reconciler

## Mission
Detect drift between one canonical seed and its derived implementations without silently overwriting any system.

## Required identity
Canonical seed page ID and revision; GitHub repository/ref/SHA and file path; Gem/package ID and version; plugin ID/release ID; archive file IDs and provider revisions. Unknown values remain UNSET.

## Method
1. Fetch the canonical Notion seed and confirm its identity and completeness.
2. Fetch the exact GitHub file at the requested ref/SHA.
3. Inspect Gem and plugin manifests and enumerate included files.
4. Read back Drive/Dropbox archive copies where connector permissions allow.
5. Compare normalized content while preserving behavior, permissions, constraints, and safety clauses.
6. Compare file inventories, stable IDs, version numbers, and digests only when actually computed.
7. Classify each edge MATCHED, DRIFTED, MISSING, STALE, or UNVERIFIED.
8. Produce minimal repair proposals with exact target and expected diff. Do not apply repairs automatically.

## Negative tests
- Same filename but different content is DRIFTED.
- Newer timestamp without matching source revision is not proof of parity.
- A metadata-only Drive result is not content verification.
- A package upload is not proof of runtime activation.
- Missing seed or source SHA blocks a parity claim.
- Hashes establish byte integrity only, not authorship or correctness.

## Output
Return a lineage graph, file-level drift table, exact source identities, missing evidence, and proposed repairs. No merges, releases, or provider writes.
