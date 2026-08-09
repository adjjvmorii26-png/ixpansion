---
name: observability-engineering
description: 'Add or review IXPANSION telemetry, audit events, diagnostics, and operational visibility. Use when behavior is hard to inspect, workflows need evidence, or failures need actionable context.'
argument-hint: '[workflow or visibility gap]'
user-invocable: true
---

# Observability Engineering

Make important decisions and failures inspectable without exposing secrets.

## Workflow

1. Identify the operator or test question that currently lacks evidence.
2. Select the smallest useful signal: structured result, metric, audit event, or diagnostic.
3. Define stable fields, severity, correlation identifier, and redaction rules.
4. Emit evidence at decision boundaries, not in every helper.
5. Test success, failure, retry, and degraded paths.
6. Document whether the signal is in-memory, local, or persistent.

## Rules

- Never log API keys, tokens, credentials, or sensitive payloads.
- Keep audit records factual and useful for replay or diagnosis.
- Do not claim durable telemetry when state is process-local.
- Prefer deterministic signals that work offline.

## Output

Return: operator question, signal design, redaction policy, observation points,
and validation evidence.
