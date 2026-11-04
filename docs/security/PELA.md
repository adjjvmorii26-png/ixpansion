# Persistence & Evidence Lineage Audit (PELA)

**Contract version:** 1.0.0  
**Status:** Proposed; inventory and runtime verification incomplete  
**Scope:** All persistent state and all paths that may promote stored data to trusted evidence.

## Objective

Establish where state is persisted, how it moves, where trust is assigned, whether verification justifies that trust, and which invariants apply regardless of storage technology.

PELA is an investigation contract, not a claim that the repository is already compliant. Static inspection, runtime observations, and hypotheses must be labeled separately.

## Required deliverables

1. Persistence Surface Inventory (PSI)
2. Evidence Lineage Graph (ELG)
3. Trust Transition Register (TTR)
4. Evidence-Backed Findings (EBF)
5. Executable Trust Properties (ETP)
6. Reproducibility manifest (repository, commit SHA, tool/version, commands, timestamp, limitations)

## Inventory record

Each persistence surface has one stable ID. Every discovered persistent write maps to exactly one primary inventory record; shared stores may have multiple writer interfaces. Record aliases, fallback paths, and replicas explicitly.

```yaml
schema_version: "pela.inventory.v1"
component:
  id: "PS-0001"
  name: "example_store"
  module: "package.module"
  storage_type: "sqlite" # sqlite|json|jsonl|filesystem|object_store|queue|memory_snapshot|other
  location: "relative/path"
  owners: []
writes:
  - interface: "save_record"
    source: "package/module.py:10"
    data_types: ["SnapshotRecord"]
reads:
  - interface: "load_record"
    source: "package/module.py:20"
    consumers: ["package/report.py:30"]
trust_level: "cached" # untrusted|cached|verified|authoritative
provenance: "static_inspection" # static_inspection|runtime_observation|test
confidence: "confirmed" # confirmed|likely|hypothesis|unknown
```

Do not use `authoritative` merely because a database is canonical or a write succeeded. Authority must be defined by the system's policy and justified by the verification path.

## Lineage edge record

Every edge identifies the source and destination, the data structure, the transformation, and any trust-state change.

```yaml
schema_version: "pela.lineage-edge.v1"
id: "EL-0001"
source:
  location: "collector/module.py:42"
  type: "RawObservation"
destination:
  location: "store/module.py:88"
  type: "SnapshotRecord"
transformation: "normalize_and_persist"
trust_transition:
  from: "untrusted"
  to: "cached"
verification:
  integrity: "not_applicable"
  provenance: "not_checked"
  freshness: "not_checked"
evidence_refs: ["EF-0001"]
```

## Trust transition register

Every transition that changes a record's trust status must be registered, including implicit transitions in report builders and convenience APIs.

Allowed outcomes: `allowed`, `violation`, `needs_review`, `not_applicable`.

A transition to verified must name the verification procedure, the fields covered, the trust root or authorization policy, freshness semantics, and failure behavior. Missing verification is not a pass.

## Finding record

Each finding includes a unique ID, severity, confidence, affected path and symbol, concise source evidence, reachable data flow, impact, recommendation, and verification status. Separate observed facts from interpretation. Never report a runtime behavior as confirmed based on static inspection alone.

Confidence:
- **Confirmed:** directly supported by reproducible behavior or unambiguous source behavior within stated scope.
- **Likely:** multiple signals support it, but a material path remains unverified.
- **Hypothesis:** plausible and testable, not established.
- **Unknown:** evidence is insufficient.

## Executable trust properties

1. **Provenance:** no record may be promoted to verified without required origin metadata.
2. **Integrity:** failed integrity validation blocks trust assignment and trusted reporting.
3. **Freshness:** expired data cannot satisfy a live-state request.
4. **Isolation:** readers cannot observe partially committed records; concurrency semantics are tested.
5. **Identity:** distinct observations retain distinct identity even when payloads match.
6. **Reporting:** reports preserve observed, cached, verified, and unknown as distinct states.
7. **Non-substitution:** cache hits cannot satisfy verification requirements without a separate, explicit verification operation.
8. **Failure closure:** missing, malformed, or unavailable verification evidence fails closed for trust promotion.
9. **Fallback consistency:** alternate paths, such as temporary-directory fallbacks, cannot silently create divergent authoritative state.
10. **Audit reproducibility:** each finding points to a repository commit and source location.
11. **Semantic preservation:** storage, cache status, integrity, freshness, verification, and authority remain separate dimensions; no component silently promotes one dimension based on another.

## Semantic preservation model

Do not model trust as one linear enum. A record may be cached and integrity-valid while stale, or persisted while its origin remains unknown. Track these dimensions independently:

- **Origin:** unknown or identified, with provenance metadata.
- **Storage:** transient, persisted, or cached.
- **Integrity:** unchecked, valid, or invalid.
- **Freshness:** current, stale, or unknown relative to a declared use-specific TTL/clock policy.
- **Verification:** unverified, verified, or failed, naming the exact checks and scope.
- **Authority:** non-authoritative or authoritative for a specific claim under an explicit policy.

A successful check in one dimension must not silently change another. In particular, integrity is not factual truth; persistence is not provenance; recency is not liveness; cache presence is not verification. Reports must preserve these dimensions or clearly declare any lossy projection.

## Acceptance criteria

PELA is complete for a declared scope only when:

- Every discovered persistent write maps to one inventory entry.
- Every known read and consumer is linked to its store or upstream producer, or marked unresolved with a reason.
- Every trust transition has an explicit decision and supporting evidence.
- Every persisted data type declares its semantic dimensions, and no implicit promotion between storage, integrity, freshness, verification, and authority is found within the declared scope.
- Every finding contains a confidence label and reproduction/inspection method.
- Every trust property has a test or a documented reason it cannot be automated.
- Tests cover positive and negative cases, including tampering, stale data, malformed metadata, concurrency, duplicate payloads with distinct origins, and cache-hit non-substitution.
- The report states the exact commit, commands executed, tests run, failures, exclusions, and unresolved questions.

A zero-finding report is not accepted if discovery coverage is incomplete.

## Investigation order

1. Establish a clean, non-destructive workspace and record the target commit.
2. Inventory persistence APIs and direct writes: database clients, file opens, serialization, repositories, queues, and custom wrappers.
3. Trace representative write paths to all readers and report consumers.
4. Search for trust assignments and cache-to-truth conversions.
5. Inspect schemas, identities, TTL/freshness, provenance, transactions, locking, and fallback behavior.
6. Write targeted regression tests before applying hardening changes.
7. Re-run discovery and compare inventories to catch newly introduced persistence surfaces.

## Safety requirements

- Do not run tests that mutate tracked working data until their side effects are understood.
- Do not modify application storage or production data during discovery.
- Treat hashes as integrity signals, not proof of source authenticity or factual truth.
- Treat cache, artifact, snapshot, observation, verified state, and authoritative state as distinct concepts.
- Record limitations explicitly; do not infer complete coverage from a successful keyword search.

## Initial repository leads

These are leads for investigation, not final findings or proof of exploitability:

- `api/emergent_skills.py`: SQLite `module_dreams` persistence in `data/memories_1.sqlite`.
- `api/veinbed.py`: JSON persistence with a `/tmp` fallback.
- `api/ouroboros.py`: JSON ledger loading, sealing, and chain validation.
- `lab/runtime_vault.py`: atomic JSON replacement, hash-chained JSONL records, and verification helpers.
- `tests/conftest.py`: test setup executes `git checkout -- data/`; assess potential loss of tracked uncommitted changes before running tests.

Source-level leads must be rechecked against the target commit and complete call graph before status is upgraded.
