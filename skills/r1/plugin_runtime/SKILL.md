---
name: plugin_runtime
description: Route authorized plugin operations through a shared capability registry, approval policy, bounded retry engine, verification contract, and evidence ledger.
---

# Plugin Runtime

## Mission
Execute provider-neutral integration operations through injected, authorized adapters. Keep provider credentials and SDK sessions outside the runtime package.

## Capabilities
- `runtime:discover` — enumerate registered adapters and advertised capabilities.
- `runtime:preflight` — validate adapter, capability, target, approval class, and execution context.
- `runtime:execute` — run an operation through policy gates and bounded retries.
- `runtime:verify` — confirm write outcomes through adapter read-after-write checks.
- `runtime:evidence` — append and retrieve redacted JSONL evidence records.

## Roots
| Root | Purpose |
|---|---|
| `ixpansion_workbench/` | Provider-neutral runtime package |
| `ixpansion_workbench/runtime.py` | Registry, execution engine, policy and evidence |
| `tests/test_plugin_runtime.py` | Runtime contract and regression tests |
| `artifacts/evidence/` | Suggested durable evidence export location |

## Operating contract
- Inject adapters only after the host confirms provider authorization and target identity.
- Treat advertised connector tools as availability, not proof of account permission.
- Read operations may execute without approval; all writes require an approved context.
- Destructive and production operations require an explicit approval decision from the host policy layer. The boolean context is not an authentication mechanism.
- Retry only idempotent operations, with a hard maximum of five attempts.
- Verify writes when the adapter supports read-after-write checks.
- Record every terminal outcome. Redact credential-like fields before evidence persistence.
- Never persist credentials, provider tokens, raw environment values, or private keys.
- Never claim a provider operation happened unless an adapter actually executed it.

## Workflow

### runtime:discover
Register only adapters whose identity, permissions, and provider session have been checked by the host. Return adapter IDs and capability names.

### runtime:preflight
Resolve the exact adapter and capability. Reject unknown capabilities, missing target identity, missing approval for writes, and unsupported policy classes before invoking the provider.

### runtime:execute
Use the shared runtime. Supply only the payload required by the adapter. Do not put credentials in payloads; the provider session belongs to the adapter host.

### runtime:verify
For writes, call the adapter's verification method when declared. A successful provider response without read-after-write verification is SUCCEEDED, not VERIFIED.

### runtime:evidence
Append structured records with outcome, adapter, capability, target, attempts, message, and evidence ID. Export logs to a durable store through a separately authorized storage adapter.

## Verification
Run `python -m unittest tests.test_plugin_runtime -v`. Test approval blocking, retry bounds, no retry for non-idempotent operations, verification failure, evidence persistence, and secret redaction. Report actual command output and exit status.
