---
name: capability-contract-compiler
description: Use when converting a connector tool schema or API description into a normalized capability contract, permission classification, failure taxonomy, and executable acceptance matrix.
---

# Capability Contract Compiler

## Mission
Turn provider-specific tool schemas into a portable, reviewable capability contract. Compile the interface; do not execute it.

## Inputs
Provider and account reference (non-secret), exact tool/action name, complete input/output schema, documentation revision, intended use, permission scope, and target adapter version. Missing identity or schema remains UNSET.

## Compile procedure
1. Preserve the original schema as immutable source evidence and record its source revision.
2. Normalize operation names, required/optional fields, enums, formats, limits, and output types into a provider-neutral contract.
3. Identify whether the action is READ, REVERSIBLE_WRITE, SENSITIVE_WRITE, DESTRUCTIVE, or PRODUCTION.
4. Extract side effects, idempotency support, pagination, rate limits, retry semantics, timeout behavior, and readback capability.
5. Map provider errors into AUTH, PERMISSION, NOT_FOUND, RATE_LIMIT, TRANSIENT, CONFLICT, VALIDATION, PROTOCOL, or UNKNOWN.
6. Generate positive, boundary, invalid, permission-denied, retry, duplicate, and partial-failure acceptance cases.
7. Flag missing contract elements instead of inferring them from examples.
8. Produce a normalized contract and test matrix with links to the original schema.

## Reject conditions
- Required fields or side effects cannot be determined.
- A write action has no exact target identity or readback plan.
- Retry safety is unknown but automatic retries are proposed.
- Secrets or credential values appear in source examples.
- Documentation and runtime schema materially disagree.

## Output
Return normalized capability contract, risk tier, error taxonomy, idempotency model, readback requirements, acceptance matrix, unresolved fields, and COMPILED, INCOMPLETE, or BLOCKED verdict. Compilation is not runtime verification.
