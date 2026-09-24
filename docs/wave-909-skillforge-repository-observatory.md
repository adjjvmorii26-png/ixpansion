# Wave 909 — SkillForge Repository Observatory

Wave 909 applies the SKILLFORGE observatory model to repository structure.

It consumes a repository file manifest and produces deterministic, descriptive
signals for:

- repository surface categories
- API modules without an obvious filename-paired test
- oversized files
- documentation-surface gaps
- a replayable repository fingerprint

The module deliberately does **not** infer semantic correctness.

A missing `tests/test_x.py` is treated as a candidate blindspot, not proof that
`api/x.py` is untested. Filename pairing is only a heuristic.

## SKILLFORGE mapping

- blindspot-hunter → candidate surface gaps
- evidence-weaver → explicit evidence policy
- provenance-auditor → replayable fingerprint
- boundary-mapper → descriptive limits
- uncertainty-tracker → candidate vs proven distinction

The next wave can connect this manifest-level observatory to repository snapshots,
temporal diffs, and metamorphic checks.
