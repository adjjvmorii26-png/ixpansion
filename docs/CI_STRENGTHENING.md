# CI strengthening

1. Shard pytest: waves / core / rest (parallel jobs)
2. Actions: checkout@v5, setup-python@v6 + pip cache
3. Coverage informational → gate on `api/wave*.py` only
4. Mutation nightly non-gating
5. Path-filter skip docker on docs-only PRs
6. Keep Lab Smoke/Graft dual-track for organism PRs
