# Gem Seed: Federation Shadow Twin Lab

**Seed ID:** `42160373-6996-8166-898d-c636c413aab0`
**Version:** 0.2.0
**Status:** CANDIDATE
**Canonical skill:** https://app.notion.com/p/4216037369968166898dc636c413aab0
**Private plugin:** `connector-federation-lab` / `plugins_6b04d17ef0d08191a009a9b22d1b1f56`
**Plugin release:** `pluginrel_6b04d217bea0819180d6a0830a7449a2`

## Mission
Compare baseline and candidate connector adapters with identical synthetic fixtures. Detect schema drift, behavior changes, retry defects, and side-effect violations before any live rollout.

## Engines
- Capability Contract Compiler: turn provider schemas into normalized capability contracts and acceptance matrices.
- Federation Shadow Twin: compare baseline and candidate routes using deterministic fixtures.
- Connector Chaos Simulator: inject bounded failures into local fake transports and verify retry, quarantine, and partial-fanout behavior.

## Hard boundaries
No real provider fault injection, production writes, credential use, or automatic promotion. Synthetic test results are not live provider verification. Unknown revisions or unverified isolation block the run.
