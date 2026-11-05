# World Canvas · Gem Skill Harness

A local deterministic simulation and test surface integrated with IXPANSION's `skills/r1/` convention.

## Run

Open `index.html` in a modern browser. Choose an individual skill check or run the full suite, then export the JSON evidence report.

## Included modules

- `dual_lens`: implementation review plus adversarial review.
- `zero_copy`: boundedness, ownership, and serialization review.
- `forge_breakers`: deterministic negative tests for state invariants.

## Scenario registry

`scenario-registry.json` defines versioned, seeded scenario fixtures with stable IDs and explicit assertions. The registry is a specification and fixture catalog; the current browser UI does not yet load or execute these JSON scenarios directly. Python contract tests validate its structure and references.

## Evidence lineage

`evidence-contract.json` defines the minimum lineage fields for future evidence producers: skill and scenario versions, source commit, runtime, execution mode, timestamp, and named check outcomes. Existing browser reports are not retroactively upgraded or authenticated by this contract.

## Boundaries

No Gemini API is called. No external service or device is controlled. The harness demonstrates local checks only; it does not establish real-world validity or model compliance. A future provider adapter must execute outside the browser, keep credentials server-side, and label provider/model identity separately from local checks.

## Evidence

Current browser reports include schema version, timestamp, world tick, state hash, and per-check PASS/FAIL. Hashes are fingerprints, not signatures or proof of authenticity. Missing lineage is unknown, never inferred.
