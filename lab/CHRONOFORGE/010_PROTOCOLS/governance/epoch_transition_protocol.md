# Epoch Transition Protocol (ETP-1)

## Goal
Move from epoch E_n to E_{n+1} (or E∞) without silent drift (INV-01), preserving identity continuity (INV-05) and proof non-erasure (INV-02).

## Preconditions
1. Target suite params under `020_CRYPTO_SUITES/<target>/`
2. Governance quorum (dual control minimum)
3. Invariant set root verified
4. Current epoch Merkle root sealed

## Phases

### Phase 0 — Announce
`EPOCH_TRANSITION_ANNOUNCE` + testament

### Phase 1 — Parallel Accept
Accept both suites during grace window; new bindings prefer target

### Phase 2 — Identity Migration
`ROTATING → MIGRATED`; dual-control signatures on migration map root

### Phase 3 — Archive Seal
Seal E_n root; open E_{n+1} manifest namespace

### Phase 4 — Deprecate
Reject pure E_n after grace; `EPOCH_TRANSITION_COMMIT` testament

### Phase 5 — Emergency (E∞)
Break-glass; mandatory post-hoc audit; named succession roles

## Abort
Observe-only; no partial identity commit without Phase 2 dual control.
