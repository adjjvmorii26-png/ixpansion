# Wave 905 — Lineage Graph

Wave 905 turns Wave 904 evidence records into a deterministic provenance graph.
It answers "where did this experiment come from?" without assigning truth,
confidence, or quality to any branch.

Nodes represent evidence records. A parent reference creates a
`derived_from` edge. Roots identify experiments with no recorded parent.
