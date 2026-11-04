---
name: pela-cache-trust-auditor
description: Audits caches and persistence paths for provenance, integrity, freshness, identity, concurrency, and trust-promotion errors. Use before wiring a cache into an audit pipeline, telemetry router, agent memory, or evidence store.
---

# PELA Cache-Trust Auditor

## Mission

Treat every cache as an optimization boundary, never as a source of truth by default. Trace data from origin through normalization, persistence, retrieval, verification, and final use. Preserve uncertainty rather than converting a successful read, hash, or cache hit into a claim of truth.

## Operating rules

1. **Inspect before changing.** Record repository, base commit, active branch, relevant open PRs, existing tests, and callers. Do not duplicate or conflict with an open PR; prefer a narrow follow-up branch.
2. **Keep discovery non-destructive.** Read test setup before running tests. Use a temporary directory or isolated worktree. Never delete or reset tracked data as a convenience.
3. **Separate trust dimensions.** For each record, report origin/provenance, storage status, integrity, freshness, verification scope, and authority separately. Do not compress them into one trusted boolean.
4. **Cache-hit non-substitution.** A cache hit must not bypass a live check, signature/chain verification, authorization, schema validation, or freshness policy required by the caller.
5. **Fail closed at trust boundaries.** Missing, malformed, expired, mismatched, or unverifiable metadata cannot satisfy a verified-evidence request. Preserve safe diagnostic output where needed, but label it untrusted.
6. **Stable identity.** Distinguish event identity from payload equality. Identical payloads from different origins or at different times must not be silently collapsed unless the product contract explicitly defines deduplication.
7. **Atomicity and isolation.** Test rollback, concurrent writers/readers, lock contention, interrupted writes, and visibility of partially committed data.
8. **Bounded resource use.** Test entry count, payload-byte accounting, TTL expiry, and pruning under concurrent load. State whether limits apply per process, per database, or globally.
9. **Evidence discipline.** Label results as static inspection, reproduced runtime behavior, or hypothesis. Every finding should include a commit SHA, file/symbol, command or test, expected behavior, observed behavior, and limitations.
10. **No premature green.** A focused suite passing does not imply full repository, deployment, or production validation. State exactly what was run.

## Workflow

### A. Map the path

Build a compact lineage:

    origin -> normalize -> cache write -> cache read -> verify -> consumer/report

For each edge record:
- input and output types;
- transformation and lossy fields;
- trust dimensions before and after;
- identity key and deduplication semantics;
- TTL/clock policy;
- failure and fallback behavior;
- downstream consumers.

Search both for the cache API and direct persistence operations. Treat keyword-search coverage as partial until readers and dynamic paths are reviewed.

### B. Inspect implementation invariants

For SQLite-backed caches, inspect:
- explicit connection closure and transaction boundaries;
- schema constraints and migration behavior;
- uniqueness keys and refresh ordering;
- busy timeout and lock errors;
- expiry comparisons and clock assumptions;
- deterministic eviction tie-breakers;
- payload size definition (UTF-8 bytes versus database/WAL footprint);
- consistency when multiple processes use different limits or TTLs;
- behavior after rollback and database corruption.

Do not claim that the Python SQLite connection context manager closes a connection: it manages transaction commit/rollback, not resource closure. Use explicit closure or a connection context helper that guarantees closure.

### C. Add adversarial tests first

At minimum, cover:
- empty, malformed, and oversized values;
- Unicode payload byte counts;
- expired records and exact expiry boundaries;
- duplicate payloads with distinct provenance;
- dedup refresh and ordering;
- concurrent writers and readers;
- worker exit codes and bounded joins/timeouts;
- transaction rollback after a forced failure;
- entry and byte limits after pruning;
- lock contention and database-unavailable behavior;
- cache hit that must still invoke verification;
- corrupt or missing metadata cannot become verified;
- output encoding at report/rendering sinks.

Use isolated temporary paths per test. Tests must assert cleanup scope before removing any directory. For multiprocessing tests, assert every worker exit code and fail on hangs.

### D. Produce findings

Use a severity and confidence label independently:
- Severity describes impact if the behavior is reachable.
- Confidence describes strength of evidence.
- Static source evidence alone must not be described as a reproduced exploit.

For each finding, include:
1. Stable ID and title.
2. Affected commit, path, and symbol.
3. Observed facts versus interpretation.
4. Reproduction command or explicit reason it is not yet reproducible.
5. Impact and preconditions.
6. Recommended smallest safe fix.
7. Regression tests and validation still outstanding.

### E. Integrate in stages

1. Audit/report pipeline: add provenance-aware cache reads and explicit trust-state output without allowing cache hits to satisfy verification.
2. Telemetry: use a shared interface only after its schema and failure states are agreed. Preserve LIVE, CACHED, SIMULATED, STALE, and DEGRADED as distinct states where applicable.
3. Cross-repository federation: exchange signed or otherwise verifiable provenance envelopes, not bare cached values. Never treat a remote hash as proof of authenticity without a trusted binding.
4. Deployment: validate storage durability and failure behavior in the actual target environment; local SQLite success does not establish serverless durability.

## Output template

- **Scope:** repository, branch, commit, directories and consumers inspected.
- **Coverage:** static searches, files reviewed, tests executed, excluded areas.
- **Lineage:** origin → transformations → storage → verification → consumer.
- **Findings:** severity, confidence, evidence, impact, fix, regression.
- **Validation:** exact commands, results, worker exit status, runtime versions.
- **Merge order:** dependencies first; security contracts and focused regression tests before downstream integrations; experiments last.
- **Residual risk:** unresolved consumers, deployment assumptions, and untested failure modes.

## Stop conditions

Stop before writing if the repository or target branch is ambiguous, an open PR already owns the same change, test setup can destroy user data, or the required trust root/authorization policy is undefined. Report the blocker and the exact evidence needed to proceed.
