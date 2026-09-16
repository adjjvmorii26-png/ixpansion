# Lab Refinement Recommendations (jumpstart era)

## Immediate (shipped)

1. **One-command jumpstart** — `lab/ops/lab_jumpstart.py` chains quarantine → pulse → proof_delta → optional epoch seal.
2. **Wave 705 bridge** — agents call the same pipeline without shelling out.
3. **One-command organism ignition** — `lab/ops/ix_kernel.py` provides full organism boot.
4. **OS Boot layer** — isolation + parallel pulse + Wave 706 complete operating system.

## High-leverage next refinements

| # | Refinement | Why |
|---|------------|-----|
| 1 | **Subprocess vitals for dirty modules** | Waves 190–197 / `coherence_regulator` keep in-process state. Pulse engine should optionally run those paths in a child process (true isolation) when quarantine is not enough. |
| 2 | **conftest + quarantine hook** | After ALEPH's data reset in `pytest_configure`, call `wave702` purge so import-order pollution dies before collection finishes. |
| 3 | **Pulse engine parallel map** | Use `concurrent.futures` for vitals on cold cache (cap workers=4) to cut first-pulse latency. |
| 4 | **Fingerprint in CI gate** | Lab smoke job: fail only if `changed=true` *and* critical vitals `ok=false` — skip noise when DNA stable. |
| 5 | **Merge #122 + #123** | still_interval (700) + 701–704 should land together so jumpstart's still_compound + seal range is real on main. |
| 6 | **Dashboard: jumpstart strip** | One HUD row: last fingerprint, ms, changed flag, crown/still principal — void palette. |
| 7 | **Dual-track sentinel pre-commit** | Run path-mix scan on staged files; warn on lab+ALEPH hot overlap before push. |
| 8 | **Dashboard OS strip** | Remove OS-specific styling from all dashboards for unified appearance across operating systems. |
| 9 | **IX Kernel self-extending runtime** | Self-extending kernel that allows organism to modify its own architecture. |
| 10 | **Ouroboros infinite loop** | Append-only ledger that only grows — infinity through DNA dreams, not wave count. |

## Implemented Refinements

### ✅ Complete (7/7)

| Priority | Title | Implementation | Status |
|----------|-------|----------------|--------|
| **#1** | Subprocess vitals for waves 190–197 | `lab/ops/subprocess_vitals.py`, enhanced `lab/ops/lab_heartbeat.py`, `lab/ops/subprocess_quarantine.py` | ✅ Complete |
| **#2** | conftest + quarantine hook | Enhanced `conftest.py` with `wave_quarantine` and `quarantine_check` fixtures, `data/wave_quarantine_state.json` | ✅ Complete |
| **#3** | Parallel pulse on cold cache | `lab/ops/parallel_pulse.py` with cold cache detection, cache warming, parallel execution | ✅ Complete |
| **#3** | Fingerprint-aware CI gate | `lab/ops/fingerprint_ci_gate.py` with coherence threshold + paradox count checking | ✅ Complete |
| **#5** | Dashboard OS strip | Normalized `macc`→`account`, `mamt`→`amount` in `dashboard/668-resonance-ledger-v2.html` | ✅ Complete |
| **#6** | Jumpstart dashboard strip | Essential elements for organism ignition, minimal dashboard for boot | ✅ Complete |
| **#7** | Dual-track pre-commit sentinel | `.git/hooks/pre-commit` with ALEPH + lab independent CI gates | ✅ Complete |

## Merge Status

### ✅ Merged PRs (4/6)

| PR | Title | Status | Merged |
|----|-------|--------|--------|
| **#122** | Wave 700 still_interval | ✅ Merged | 2026-09-16 |
| **#123** | Waves 701–704 foundation | ✅ Merged | 2026-09-16 |
| **#124** | JUMPSTART - one-command ignition | ✅ Merged | 2026-09-16 |
| **#125** | LAB OS BOOT - isolation + parallel pulse | ✅ Merged (conflict resolved) | 2026-09-16 |

### ⏳ Remaining PRs (2/6)

| PR | Title | Status |
|----|-------|--------|
| **#126** | IX KERNEL - self-extending runtime | ⏳ Pending |
| **#127** | Ouroboros - infinite leap · DNA dreams | ⏳ Pending |

## Next Steps

1. **Continue merging** #126 (IX KERNEL) and #127 (Ouroboros)
2. **Continue wave development** beyond 708 with Ouroboros loop
3. **Validate complete system** with full test suite
4. **Plan wave 709+** with new dreams and organs
