# IXPANSION Weekly Status — 2026-11-23

**main:** ed553794 (approx)
**open PRs:** ~20+ (many drafts, stacked federation/workspace)
**merges (7d):** #427 (Telegram token fail-closed, 2026-11-21)
**wave frontier (main):** Wave 767 (mycelial_truths)
**failed CI:** none observed on recent heads; lab-smoke & ALEPH CI green on checked PRs

## Dual-track
- Lab smoke/graft: path-filtered, lab/** only
- ALEPH full monorepo CI: on main / PRs to main
- Risks: long-lived experiment PRs (#359, #361 auth-store), stacked feature branches, potential lab notes leaking into production routes

## Next high-leverage
1. Close or promote auth-store durable contract (#361)
2. Automated dual-track contamination sentinel (beyond Wave 686)
3. PR stack visualizer / merge-readiness gate for stacked PRs

Generated autonomously by steward pulse.
