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
