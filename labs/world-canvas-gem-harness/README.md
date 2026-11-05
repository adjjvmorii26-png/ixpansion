# World Canvas · Gem Skill Harness

A local deterministic simulation and test surface integrated with IXPANSION's `skills/r1/` convention.

## Run
Open `index.html` in a modern browser. Choose an individual skill check or run the full suite, then export the JSON evidence report.

## Included modules
- `dual_lens`: implementation review plus adversarial review.
- `zero_copy`: boundedness, ownership, and serialization review.
- `forge_breakers`: deterministic negative tests for state invariants.

## Boundaries
No Gemini API is called. No external service or device is controlled. The harness demonstrates local checks only; it does not establish real-world validity or model compliance.

## Evidence
Reports include schema version, timestamp, world tick, state hash, and per-check PASS/FAIL. Hashes are fingerprints, not signatures or proof of authenticity.
