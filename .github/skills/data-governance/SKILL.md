---
name: data-governance
description: 'Review IXPANSION data usage, privacy, retention, and handling boundaries. Use when collecting, transforming, storing, logging, transmitting, or exposing user, workflow, telemetry, configuration, or model data.'
argument-hint: '[data flow or usage question]'
user-invocable: true
---

# Data Governance

Keep data use necessary, bounded, inspectable, and consistent with the
execution boundary. Treat secrets and sensitive payloads as data risks even
when they are not stored permanently.

## Workflow

1. Map the data flow from input to output, including logs, caches, queues, and external calls.
2. Classify each field as public, internal, sensitive, or secret.
3. State the purpose and minimum data required for each processing step.
4. Remove, redact, hash, or aggregate data that is not required downstream.
5. Define access, retention, deletion, and persistence behavior for each store.
6. Verify that simulated, process-local, and durable paths are clearly distinguished.
7. Test malformed input, secret redaction, unauthorized access, and retention behavior where applicable.
8. Document user-visible data handling and any external transfer or optional integration.

## Safety boundaries

- Never log credentials, authorization headers, tokens, private keys, or raw sensitive payloads.
- Prefer data minimization over collecting fields for possible future use.
- Keep test fixtures synthetic and safe to commit.
- Do not send data to optional external services without explicit configuration and a clear boundary.
- Do not claim deletion, privacy, encryption, or persistence guarantees that the code does not enforce.
- Preserve only the identifiers and audit facts needed for bounded replay, diagnosis, or accountability.

## Report

Return: data-flow map, classification, purpose, minimization decisions,
retention and access rules, validation evidence, external-transfer boundary,
and remaining privacy or operational risk.
