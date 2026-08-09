---
name: multi-layer-autonomous
description: 'Design, implement, and validate multi-layer autonomous behavior in IXPANSION. Use when a task spans operators, forge agents, trust, safety, fabric, lattice, federation, persistence, or API/CLI orchestration; when asked to make the system intelligent, autonomous, self-improving, distributed, or end-to-end.'
argument-hint: '[goal, workflow, or capability to make autonomous]'
user-invocable: true
---

# Multi-Layer Autonomous Builder

Turn a high-level capability request into a bounded, inspectable workflow that
coordinates IXPANSION's layers without pretending that a simulator is a
production distributed system.

## Operating Model

Treat autonomy as a feedback loop with explicit boundaries:

```text
intent -> plan -> capability selection -> trust/safety gate -> execution
   ^                                                            |
   +----------- telemetry <- evaluation <- audit ---------------+
```

Map the request to the smallest set of these layers:

- **Operators:** CLI, API, dashboard, configuration, feature flags, and metrics.
- **Forge:** PSO, ACO, island, federated, or other agent executors.
- **Trust and safety:** namespaced trust, EMA updates, human gates, audit records,
  dry-run behavior, URL allowlists, and quarantine decisions.
- **Fabric:** lattice allocation, leases, CRDT state, queues, gas limits, and
  shard or transport boundaries.
- **SI/federation:** cross-node state, migration, retries, degraded operation,
  and explicit simulated-versus-real transport contracts.

Do not invent a new layer when an existing module owns the behavior. Keep the
orchestration inspectable: a caller should be able to see the selected plan,
constraints, trust decision, execution result, and audit/telemetry outcome.

## Autonomous Workflow

1. **Translate the goal.** State the requested outcome, inputs, outputs, success
   signals, failure modes, and whether execution is read-only, simulated, or
   externally effectful.
2. **Trace ownership.** Start at the nearest CLI, API route, runtime, or test;
   follow it to the code that computes state or makes decisions. Read the
   neighboring tests before editing.
3. **Build a layer contract.** For every touched layer, record its input,
   output, invariant, and observation point. If a layer is planned but absent,
   implement the smallest explicit seam or report it as a blocker; do not imply
   that planned architecture is already available.
4. **Choose bounded autonomy.** Define budgets for iterations, retries, time,
   work allocation, and external calls. Prefer deterministic offline behavior
   and dependency injection. Require a human gate for deployment, secret
   rotation, destructive actions, or changes outside the allowlist.
5. **Implement the vertical slice.** Wire the smallest end-to-end path through
   the owning abstractions. Preserve public APIs unless the request requires a
   contract change. Keep simulated transport and production transport visibly
   separate.
6. **Add feedback.** Expose useful telemetry and evaluate outcomes against the
   success signals. Update trust only from observable results, clamp updates to
   documented bounds, and quarantine or degrade safely when health, capacity,
   trust, or freshness falls below the local floor.
7. **Test the boundaries.** Cover the happy path, malformed input, budget
   exhaustion, unavailable capacity, stale or untrusted nodes, partial failure,
   retries, and idempotent replay where applicable. Mock network and secrets.
8. **Validate in widening circles.** Run the narrowest relevant test first,
   then the full test suite, compilation/lint checks, and `git diff --check`.
   Exercise API contracts with `TestClient`; use a live server only for a local
   smoke check.
9. **Report the autonomy honestly.** Summarize the layers changed, decisions
   made, safety gates, evidence from validation, remaining limitations, and
   exact next actions. Never claim multi-host, self-improving, persistent, or
   production-safe behavior without code and tests proving it.

## Decision Rules

- Autonomous means the system can select and execute bounded next steps from
  observable state; it does not mean bypassing authorization or human gates.
- Prefer local deterministic plans when no API key or network is configured.
- Fail closed for missing trust, invalid leases, unsafe URLs, exceeded budgets,
  and unavailable required capacity.
- Make retries idempotent and attach a stable task or workflow identifier when
  state can be written.
- Keep audit events useful without logging credentials, tokens, or sensitive
  payloads.
- Preserve user changes in a dirty worktree and never commit, push, reset, or
  create a pull request unless explicitly requested.

## Completion Checklist

- [ ] Goal and execution boundary are explicit.
- [ ] Each touched layer has a contract and an observation point.
- [ ] Budgets, trust checks, safety gates, and failure behavior are implemented.
- [ ] Offline or simulated behavior remains usable without credentials.
- [ ] Focused boundary tests and relevant regression tests pass.
- [ ] Documentation and API/CLI examples match the implementation.
- [ ] Limitations distinguish the scaffold from production capabilities.