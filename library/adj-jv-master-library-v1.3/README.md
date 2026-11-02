# Library Core v1.3 — Integrity Epoch

Governed knowledge catalog: stable IDs, evidence lineage, contradiction atlas, proof objects. No Canon without a trail of proof.

## Archivist of Coherence

CI gate for unique/reserved IDs, shelf-prefix consistency, one-level evidence advances, versioned references, provenance, and explicit contradiction accounting. Not a daemon.

## Evidence lifecycle

| State | Label | Required metadata |
|---|---|---|
| `idea` | Spark | `origin.source`, `origin.ref` |
| `hypothesis` | Claim | expected impact, falsifiable condition, related entries |
| `implemented` | In the wild | code refs, repository links, branch/PR, outcome |
| `tested` | Trialed | test refs, metrics, failure modes |
| `verified` | Canon | version pin, known limitations, contradiction watchlist |

Order: idea → hypothesis → implemented → tested → verified. Each PR advances at most one level. Downgrades need reason + trigger (contradiction, bug, new_data, design_change, deprecation).

## Contradiction Atlas

Conflicts are `frontier` records (entries, dimension, shelf, status, resolution path, follow-up). Atlas starts empty; no invented conflicts.

## Golden specimen: G-03

`G-03 — Evidence Lineage` stays `implemented` until real test-run evidence is recorded. Branch/PR refs document location, not a passing run.

## Run locally

```bash
python library_validator.py
python -m unittest -v
python library_validator.py --base-ref origin/main
```

## No lore without proof

Evidence labels are process claims, not cryptographic proof. Reviewers and CI verify referenced artifacts/runs.

## Proof-bearing substrate

Proof objects follow `proof.schema.json` in `proof_objects`. Bind proof ID → entry/claim, artifact URI + SHA-256, verifier, reproducible command, env + lockfile digests, result. CI proofs also bind run ID/URL, workflow, conclusion, commit SHA.

1. Offline: schema, ownership, digests, reproducibility, Canon proof links.
2. CI-backed: hash local `repo://` artifacts; verify Actions runs and artifact ZIPs.

## Canon promotion gate

`python canon_gate.py --entry G-03` — dry-run only. Requires `tested`, version pin, limitations, watchlist, and a passing proof. Never auto-edits the manifest.

Current: `G-03` is `implemented`; `proof_objects` empty until claim-specific evidence is attached.

## Squirrel Cache

`squirrel_cache.py` — stdlib-only tagged snippet cache (`SquirrelCache`, `squirrel_hoard` / `squirrel_retrieve`). Atomic writes, SHA-256 digests, legacy list migration. Digest = byte integrity, not truth. Tests: `python -m unittest -v`.
