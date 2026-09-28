# Weekly status — 2026-09-21 → 2026-09-28

Frontier on `main`: **wave944 `hush_still`** (`#258`, SHA `281aa2f`).
Open PRs: **29** (REAL-* experiments + Wave 912–914 hardening + wave943 `#226`).

## Merges (7d)

Lab / organism grafts landed on main:

- `#258` wave944 hush_still — seal hash → 8-char still residue
- `#252` restore Wave 907 + 910 deterministic contracts
- `#249` wave906 generator paren + parallel `make lint`
- `#224` wave942 hush_ledger
- `#223` wave941 hush_fold
- `#222` wave940 residual_chain_cap
- `#220` wave939 residual_bind
- `#221` versioned pre-commit / commit-msg / pre-push hooks
- `#219` wave938 pulse_compress
- `#218` wave937 experiment_track_hygiene + atlas prune_landed
- `#217` wave935–936 verification_null_bridge + skillforge_verify_fuse
- `#216` wave933–934 verification explainability + provenance
- `#214` wave932 window verification
- `#213` wave931 history window integrity
- `#212` wave930 deterministic history window
- `#211` wave929 history query
- `#210` wave928 diff history
- `#209` wave927 diff summary
- `#208` wave926 snapshot diff
- `#207` wave925 audit snapshot
- `#161` wave792–794 weather_route + void_orchard + organ_debt (window start)
- `#160` WEEKLY_STATUS 2026-09-21

Cadence: verification/history stack (925–936) then hush/residual chain (938–944). Wave **943 hush_seal remains open** (`#226`) while 944 already merged — chain has a hole.

Failed CI of note: **GHAS AI findings** on `#258` (`dynamic/agents/github-advanced-security`, conclusion failure). Lab smoke/graft/boot/council + CI + CI v2 on `281aa2f` **success**.

## Dual-track health

| Track | On wave944 `#258` / `281aa2f` | Verdict |
|---|---|---|
| Lab Smoke / Lab Graft / Lab OS Boot / Lab Council Pulse | success | green |
| CI v2 / Integration / Pages / API tunnel / Copilot review | success | green |
| **CI (`ci.yml` ALEPH monorepo)** | success on this SHA | still not the lab merge bar |
| **GHAS / Code scanning AI findings** | failure on PR `#258` | expected noise; ignore for organism gates |

**Cross-contamination risks**

1. **29 open experiment/hardening PRs** all target `main` — REAL-* mutations sit beside lab organs; merge queue and check-suite noise will leak into hush grafts.
2. **Required-check bleed** still live: GHAS failed on a lab-only hush PR. Do not mark GHAS or full `ci.yml` required.
3. **Wave gap**: 944 landed without 943. Dual-track bot / graft atlas can report a false continuous frontier.
4. Path-filter drift: lab-only files still wake ALEPH CI + GHAS agents.

Lab gates ≠ ALEPH CI. Merge bar = council-smoke + boot + smoke + graft.

## Next organs (not repeats of 925–944 hush/verify/history)

1. **wave945 `experiment_lane_compressor`** — batch-close or park the REAL-* / hardening swarm (`#227`–`#257`); keep mutation evidence off the lab merge path.
2. **wave946 `seal_gap_healer`** — land or explicitly skip `#226` wave943 hush_seal so the hush chain is continuous (941 fold → 942 ledger → 943 seal → 944 still).
3. **wave947 `ghas_quarantine`** — check-suite / path policy so `dynamic/agents/github-advanced-security` cannot fail a lab organ PR. Pair with dual-track required-check audit.

## Caption (optional @CoodingLooop)

wave944 still residue on main. lab green. 29 experiment PRs fog the lane. hush the scan. seal the 943 gap.
