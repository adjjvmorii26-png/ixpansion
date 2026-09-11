# Helix Bridge · SPEC v0.1

## Purpose
Probe organism portals (ethics-first) → `constellation.json` for status/captions.

## Protocol HB-1
probe → aggregate ok flags → write constellation → optional proof_ledger append

## Invariants
- Ethics fail ⇒ constellation ok=false
- Append-only ledger
- Missing portal = skip, not crash
