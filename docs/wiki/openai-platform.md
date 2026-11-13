# OpenAI Platform Integration

## Purpose

OpenAI Platform is the control plane for IXPANSION model/API access. It is not a credential vault for documentation and must not be treated as a general-purpose database.

## Project layout

Use separate Platform projects for distinct runtime boundaries when isolation is needed, for example:

- **IXPANSION Core**: core application and orchestration workloads.
- **IXPANSION Labs**: experimental agents, evaluations, and short-lived prototypes.
- **IXPANSION CI**: narrowly scoped automated checks, if a separate project is justified.

Project names and IDs must be confirmed from the connected Platform account before use. Do not invent project IDs or silently create keys.

## Credential handling

1. Create project-scoped keys through the approved OpenAI Platform setup flow.
2. Store keys only in the deployment provider's encrypted environment-variable store or an approved local secret manager.
3. Use environment variable names such as `OPENAI_API_KEY`; never store their values in Git, Notion, Drive, issue comments, or logs.
4. Use separate keys for local development, CI, and production.
5. Rotate or revoke keys after exposure or ownership changes.
6. Set usage limits and alerts appropriate to the workload.

## Model and evaluation policy

- Record model identifier, prompt/template revision, date, and evaluation dataset version for reproducible experiments.
- Label mock or offline runs as **SIMULATED**.
- Keep latency, token usage, error rate, and cost measurements with each benchmark.
- Do not infer model availability from a remembered model name. Query current Platform capabilities before pinning a model.

## Integration status

This document defines the integration contract. It does not claim that an API key has been created, installed in a runtime, or tested. Those are separate actions requiring a selected project and an explicit secret destination.
