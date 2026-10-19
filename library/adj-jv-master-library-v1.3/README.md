# Library Core v1.3 — Integrity Epoch

**Release narrative**

This was the release where the ADJJV Master Library stopped being a pile of clever ideas and became a governed space. We introduced a manifest with stable IDs and explicit evidence lineage, a validator that refuses to accept silent contradictions, and a regression suite that treats knowledge like code: testable, breakable, fixable.

From this point on, no entry becomes “Canon” without a trail of proof.

## Archivist of Coherence

The validator is the gatekeeper for changes to these shelves. It enforces unique and permanently reserved IDs, shelf-prefix consistency, evidence-state lineage, versioned references, required provenance, lifecycle-specific metadata, and explicit contradiction accounting. It is invoked by CI; it is not a daemon and does not independently prevent direct edits outside governed workflows.

## Evidence lifecycle

| State | Label | Required metadata |
|---|---|---|
| `idea` | Spark | `origin.source`, `origin.ref` |
| `hypothesis` | Claim | expected impact, falsifiable condition, related entries |
| `implemented` | In the wild | code refs, repository links, branch/PR, outcome |
| `tested` | Trialed | test refs, metrics, failure modes |
| `verified` | Canon | version pin, known limitations, contradiction watchlist |

Evidence advances in this order: idea → hypothesis → implemented → tested → verified. Every state event requires version, fromstate/tostate, UTC timestamp, actor, change/reason, and evidence reference. Each PR may advance an entry at most one level. Downgrades require a reason and a recognized trigger (contradiction, bug, new data, design change, or deprecation).

## Contradiction Atlas

Contradictions are frontiers, not automatically errors. Each conflict must be represented by a `frontier` atlas record naming at least two entries, the dimension, shelf, status, resolution path, and follow-up. Both entries must declare the conflict. Resolved conflicts need a resolution reference; active conflicts need a follow-up. The atlas is currently empty; no conflict is invented merely to populate it.

## Golden specimen: G-03

`G-03 — Evidence Lineage` is the canonical worked example for the lifecycle contract. It remains `implemented`, not `tested` or `verified`, until actual test-run evidence is recorded. The branch and PR references document where the implementation lives; they do not certify a passing run.

## Run locally

```bash
python library_validator.py
python -m unittest -v
python library_validator.py --base-ref origin/main
```

The optional base comparison rejects evidence jumps greater than one level and requires a matching atlas record for newly introduced contradiction edges.

## No lore without proof

Manifest evidence labels are claims governed by process, not cryptographic proof. Reviewers and CI must verify the referenced artifact or run. Never promote an entry because the desired status is narratively appealing.

## Proof-bearing substrate

Proof objects use `proof.schema.json` and are stored in the manifest's `proof_objects` registry. Each object binds a proof ID to a specific entry and claim, artifact URI and SHA-256 digest, verifier/version, reproducible command, environment description, a repository lockfile URI and its SHA-256 digest, and observed result. CI proofs additionally bind an immutable Actions run ID/URL, workflow name, conclusion, and commit SHA.

The contract has two layers:

1. **Offline structural validation** checks schema fields, IDs, claim ownership, digest format, reproducibility declarations, and whether a Canon entry references a passing proof for itself.
2. **CI-backed validation** hashes local `repo://` artifacts and environment lockfiles, downloads and hashes referenced GitHub Actions artifact ZIPs, and queries the Actions API to confirm each referenced CI run completed successfully on the exact declared commit and workflow.

A digest proves byte identity, not the truth of the claim. A CI success proves that a particular workflow passed at a particular revision, not that every statement in the library is universally true. Proofs must therefore state the claim and limitations narrowly.

## Canon promotion gate

Run `python canon_gate.py --entry G-03` to perform a **dry-run eligibility check**. The entry must first be `tested`, must include a version pin, known limitations, contradiction watchlist, and at least one proof reference that resolves to a passing reproducible CI/test proof. The gate never edits the manifest; promotion remains a separate, reviewable change with a new history event.

Current state: `G-03` remains `implemented`; `proof_objects` is empty; no entry is Canon. This is intentional until genuine, claim-specific evidence is attached.


## Squirrel Cache — tagged knowledge snippets

`squirrel_cache.py` provides a small standard-library-only cache for local snippets.
It preserves the original `squirrel_hoard(tag, snippet)` and
`squirrel_retrieve(tag)` helpers, and adds a `SquirrelCache` class for explicit
cache locations:

```python
from squirrel_cache import SquirrelCache

cache = SquirrelCache("cache/nuts")
cache.hoard("dark_hex", "Background: #03040A; accents: #00E5FF and #FF2BD6.")
snippets = cache.retrieve("dark_hex")
```

The versioned manifest stores unique entry IDs and SHA-256 digests. Cache files and
the manifest are written atomically; unsafe tags, missing files, malformed manifests,
and content/digest mismatches are rejected. A legacy list-shaped manifest from the
original demo is migrated on read. Importing the module does not create a cache
directory; the compatibility helper initializes its default cache lazily.

**Trust boundary:** a matching digest establishes byte integrity relative to the
manifest, not truth or evidentiary quality. Snippets must retain their own evidence
classification in the Library Core when factual claims matter.

Run its regression tests from this directory with `python -m unittest -v`.
