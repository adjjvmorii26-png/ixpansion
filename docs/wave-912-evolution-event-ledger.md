# Wave 912 — Evolution Event Ledger

Wave 912 turns temporal repository changes into a deterministic event ledger.

Each event keeps a stable identifier, path, change kind, descriptive
classification, and links to known evidence. Unknown evidence references are
not silently promoted into evidence.

The ledger is intentionally append-only and does not interpret unexplained
change as regression. It is a bridge between temporal diffs and later
metamorphic/evolution experiments.
