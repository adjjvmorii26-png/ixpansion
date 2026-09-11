# Decision log · 2026-09-11

## Decision
Ship **Lab Smoke** path-filtered workflow instead of waiting on full monorepo CI green for organism work.

## Why
- Full CI on PR #104 fails on lint/test/docker at monorepo scale (ALEPH/Growth surface), not because lab modules fail to compile.
- Local `lab/smoke_lab.py` is green (compile + Helix 6/6 ethics).
- Keeps organism iteration unblocked while main CI is a separate track.

## Actions taken
- Added `.github/workflows/lab-smoke.yml` (checkout@v5, setup-python@v6, `python lab/smoke_lab.py`)
- Triggers on `lab/**`, `sandbox/**`, lab branches

## Not done (intentionally)
- Did not force-merge #104/#105 while full CI red
- Did not rewrite main CI
