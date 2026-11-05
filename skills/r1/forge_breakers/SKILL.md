---
name: forge_breakers
description: Build deterministic negative tests that challenge state-machine invariants and rejected-operation isolation.
---

# Forge-Breakers

## Capabilities
- `forge_breakers:attack_matrix` — enumerate deterministic negative cases.
- `forge_breakers:execute` — run bounded, non-destructive invariant checks.
- `forge_breakers:report` — emit exact test outcomes and coverage limits.

## Roots
| Root | Path |
|---|---|
| Skill | `skills/r1/forge_breakers/` |
| Harness | `labs/world-canvas-gem-harness/` |
| Tests | `tests/skills/` |

### forge_breakers:attack_matrix
Cover coordinates below zero/above bounds, energy outside its range, duplicate IDs, capacity overflow, invalid action order, and rejected commits.

### forge_breakers:execute
Keep tests deterministic and non-destructive. Confirm rejected operations do not partially mutate committed state. Exercise undo and reset after both successful and rejected actions.

### forge_breakers:report
Report exact executed cases, pass/fail totals, and untested behavior. Never infer complete coverage from a smoke suite.
