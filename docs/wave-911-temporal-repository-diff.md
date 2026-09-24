# Wave 911 — Temporal Repository Diff

Wave 911 compares two repository manifests and records added, removed, and
modified paths with deterministic before/after fingerprints.

This is intentionally weaker than a regression detector. A structural change
is evidence that the repository changed; it is not evidence that behavior
became worse.

Future waves can enrich these records with topology, evidence-graph, contract,
and metamorphic signals to identify unexplained architectural drift.
