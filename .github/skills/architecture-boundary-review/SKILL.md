---
name: architecture-boundary-review
description: 'Review IXPANSION ownership boundaries and integration points. Use when a change spans modules, layers, agents, lattice, trust, safety, federation, API, or CLI.'
argument-hint: '[change or architecture question]'
user-invocable: true
---

# Architecture Boundary Review

Find the module that owns each decision and keep changes at the narrowest
stable boundary.

## Workflow

1. Trace from the nearest route, command, runtime, or test to the code that computes or mutates behavior.
2. Map each touched boundary with its inputs, outputs, invariants, and failure behavior.
3. Check whether an existing abstraction already owns the requested behavior.
4. Identify contract, persistence, trust, safety, and transport boundaries.
5. Recommend the smallest vertical slice and the tests that observe each boundary.

## Rules

- Do not add speculative layers for planned architecture.
- Keep simulated transport visibly separate from real network behavior.
- Preserve public APIs unless a contract change is required and documented.
- Call out ownership ambiguity instead of distributing logic across neighbors.

## Output

Return: ownership map, boundary invariants, proposed change surface,
contract risks, and focused test points.
