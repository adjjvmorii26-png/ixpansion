---
name: zero_copy
description: Audit serialization, cloning, payload bounds, and ownership boundaries without weakening mutation isolation.
---

# Zero-Copy

## Capabilities
- `zero_copy:map_boundaries` — inventory copies, serialization, and ownership boundaries.
- `zero_copy:optimize` — propose safe reductions with invariant proofs.
- `zero_copy:check_bounds` — verify bounded histories and payloads.

## Roots
| Root | Path |
|---|---|
| Skill | `skills/r1/zero_copy/` |
| Harness | `labs/world-canvas-gem-harness/` |

### zero_copy:map_boundaries
List each copy/serialization boundary, its purpose, cost, and mutation owner.

### zero_copy:optimize
Reduce data movement only when a clear invariant preserves transaction isolation. Keep defensive copies where callers could otherwise mutate committed state.

### zero_copy:check_bounds
Verify bounded undo history, event ledger, collection capacity, and report size. A hash is not authenticity, authorization, or lineage proof.
