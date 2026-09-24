# Wave 908 — Topology Integrity

Wave 908 adds a deterministic diagnostic layer for lineage topology.

It exposes:
- duplicate record identifiers
- self-cycles
- longer directed cycles
- orphan parent references
- the current single-parent schema limitation
- a replayable integrity fingerprint

The layer is deliberately descriptive. It does not rank branches, infer causation,
declare semantic truth, or assign quality.

Wave 908 follows the Wave 907 Branch Atlas and is intended to make malformed or
incomplete structure visible before downstream visualization or replay.
