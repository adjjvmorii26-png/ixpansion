# Wave 904 — Evidence Ledger

Wave 904 provides append-only experimental provenance. Records capture a
hypothesis, recipe, baseline digest, result digest, falsifier, optional parent,
and a deterministic record digest.

The ledger does not assign truth or confidence automatically. It preserves
evidence so later layers can inspect lineage without silently rewriting history.
