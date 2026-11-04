# IXPANSION monorepo hygiene (2026-11)

## CI truth model

1. **Empty-job / zero-duration failures on `main`**  
   Runs with `jobs: 0` and no step logs are platform dispatcher issues, not suite failures.

2. **App-level CORS**  
   Hardened allowlist middleware: unknown origins empty; wildcards raise; `Vary: Origin` always set.

3. **Ubuntu runner pin**  
   CI uses `ubuntu-24.04` through the `ubuntu-latest` → 26.04 migration (~2026-11-19).

## PR hygiene

Land order when stacking: CORS/tests → CI pin → workflow YAML (#365) → manifold (#373).

Do not merge drafts that state tests were not run.

## Vercel

- Team: `ixpansion-agents`
- Project: `ixpansion-live` (`prj_wS2Z11vKFkxuoGCjeP8hBDCAOWu0`)
- Domains: `ixpansion-live.vercel.app`
- Production deploys lag `main` until a new deploy is triggered after merge.
