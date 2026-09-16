# Lab Refinement Recommendations (jumpstart era)

## Immediate (shipped)

1. **One-command jumpstart** — `lab/ops/lab_jumpstart.py` chains quarantine → pulse → proof_delta → optional epoch seal.
2. **Wave 705 bridge** — agents call the same pipeline without shelling out.

## High-leverage next refinements

| # | Refinement | Why |
|---|------------|-----|
| 1 | **Subprocess vitals for dirty modules** | Waves 190–197 / `coherence_regulator` keep in-process state. Pulse engine should optionally run those paths in a child process (true isolation) when quarantine is not enough. |
| 2 | **conftest + quarantine hook** | After ALEPH’s data reset in `pytest_configure`, call `wave702` purge so import-order pollution dies before collection finishes. |
| 3 | **Pulse engine parallel map** | Use `concurrent.futures` for vitals on cold cache (cap workers=4) to cut first-pulse latency. |
| 4 | **Fingerprint in CI gate** | Lab smoke job: fail only if `changed=true` *and* critical vitals `ok=false` — skip noise when DNA stable. |
| 5 | **Merge #122 + #123** | still_interval (700) + 701–704 should land together so jumpstart’s still_compound + seal range is real on main. |
| 6 | **Dashboard: jumpstart strip** | One HUD row: last fingerprint, ms, changed flag, crown/still principal — void palette. |
| 7 | **Dual-track sentinel pre-commit** | Run path-mix scan on staged files; warn on lab+ALEPH hot overlap before push. |

## Architecture stance

- **Silence is the product surface** — jumpstart should stay quiet (JSON report, no audio).
- **Lab gates ≠ ALEPH CI** — jumpstart must never block monorepo full-test.
- **Compression is memory** — proof_delta skips work when DNA unchanged.

## Caption

`jumpstart · quarantine · pulse · delta · seal`
