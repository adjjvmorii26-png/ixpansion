---
name: dual_lens
description: Review IXPANSION changes through implementation and adversarial lenses, producing evidence-ranked findings.
---

# Dual Lens

## Capabilities
- `dual_lens:review` — inspect implementation correctness and contracts.
- `dual_lens:challenge` — independently search for adversarial counterexamples.
- `dual_lens:report` — rank verified findings and hypotheses separately.

## Roots
| Root | Path |
|---|---|
| Skill | `skills/r1/dual_lens/` |
| Harness | `labs/world-canvas-gem-harness/` |

### dual_lens:review
Check state transitions, invariants, accessibility, mobile interaction, error handling, and maintainability.

### dual_lens:challenge
Try invalid inputs, repeated actions, boundary coordinates, duplicate identifiers, stale state, and rendering side effects.

### dual_lens:report
Report severity, affected path, reproduction, impact, and minimal fix. Distinguish verified defects from hypotheses. A happy-path demo is not a review.
