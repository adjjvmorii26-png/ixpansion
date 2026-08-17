---
name: performance-capacity
description: 'Evaluate IXPANSION performance and resource capacity. Use when changes affect allocation, lattice work, concurrency, payload size, latency, throughput, memory, or execution budgets.'
argument-hint: '[operation or performance concern]'
user-invocable: true
---

# Performance and Capacity

Measure the limiting resource before optimizing and keep resource use bounded.

## Workflow

1. Define the operation, workload, resource budget, and acceptable signal.
2. Establish a small reproducible baseline or inspect existing measurements.
3. Locate the dominant cost using evidence rather than intuition.
4. Apply the smallest optimization that preserves contracts and safety checks.
5. Re-measure normal, empty, worst-case, and budget-exhaustion inputs.
6. Record capacity assumptions and regression thresholds.

## Safety boundaries

- Do not trade correctness, trust, or safety for speed without explicit approval.
- Preserve deterministic offline behavior.
- Avoid benchmark claims without workload, environment, and measurement details.
- Keep concurrency, queue, lease, and gas limits explicit.

## Report

Return: baseline, bottleneck, bounded change, measurements, capacity limits,
and residual risk.
