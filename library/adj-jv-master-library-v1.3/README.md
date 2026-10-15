# ADJJV Master Library v1.3

A small, dependency-free, machine-readable knowledge catalog. This is a versioned library artifact and validator, not a background service.

## Files
- `manifest.json`: canonical shelves, entries, evidence classes, relationships, and per-entry history.
- `library_validator.py`: deterministic schema/integrity checks, ID index builder, and contradiction report.
- `test_library_validator.py`: standard-library regression tests.

## Run
From this directory:
```bash
python library_validator.py
python -m unittest -v
```

## Contract
- Entry IDs are globally unique and their prefix must match the shelf ID.
- Relationship and contradiction references must resolve to known IDs.
- Evidence is one of `idea`, `hypothesis`, `implemented`, `tested`, or `verified`. These labels are assertions in the manifest, not proof by themselves.
- Each entry has a positive current version and a strictly increasing history ending at that version; every history record has a change and reason.
- Normalized title collisions are validation warnings represented as errors requiring review; they are not silently deduplicated.
- Declared contradictions are reported as review items, not auto-resolved.
- Validation does not upgrade evidence status or execute the ideas described by an entry.

## Versioning
Increment `library_version` for library-wide changes. Increment an entry's `version` and append a history record for changes to that entry. Preserve the prior history; do not rewrite it to imply a test or verification that did not occur.
