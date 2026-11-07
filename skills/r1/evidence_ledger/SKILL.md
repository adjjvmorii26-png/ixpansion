---
name: evidence_ledger
description: Record, verify, and export engineering evidence with provenance, redaction, and honest status semantics.
---

# Evidence Ledger

## Capabilities
- `evidence:record` — append an immutable operation record.
- `evidence:verify` — check evidence references and status claims.
- `evidence:export` — export a redacted report for a repository, experiment, or deployment.

## Roots
| Root | Path |
|---|---|
| Repository | `.` |
| Evidence artifacts | `artifacts/evidence/` |
| Execution logs | `logs/` |
| Workbench registry | `.workbench/plugin-registry.yaml` |

## Status vocabulary
- VERIFIED: directly observed or reproduced.
- SIMULATED: mock, fake, or simulated environment only.
- DEGRADED: partially works with a known limitation.
- PENDING: not yet verified.
- CONTRADICTED: evidence conflicts with the claim.
- NOT_RUN: execution did not occur.

### evidence:record
Append UTC timestamp, actor, adapter/tool, target, action, input digest, outcome, verification method, evidence references, and redaction notes. Never log tokens, passwords, private keys, or raw environment values.

### evidence:verify
For tests, require the exact command, exit code, concise output, and environment identity. For deployments, distinguish creation, build success, readiness, and production health. For writes, read back the resource when possible.

### evidence:export
Export only the minimum evidence needed. Store large logs as artifacts linked by stable reference and digest. Never rewrite historical evidence; append a correction event referencing the original record.
