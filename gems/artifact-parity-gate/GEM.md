# Gem Seed: Artifact Parity Gate

**Version:** 0.1.0  
**Status:** CANDIDATE  
**Canonical Notion skill:** https://app.notion.com/p/422603736996818f949cd888996e3081  
**Canonical Notion page ID:** `42260373-6996-818f-949c-d888996e3081`  
**Plugin:** connector-federation-lab v0.3.0  
**Plugin release:** pluginrel_6b04e57892688191b20e1930d3779c30

## Mission
Verify that canonical artifacts and downstream copies represent the same approved revision across Notion, GitHub, Google Drive, and Plugin Creator.

## Required evidence
- Exact source and destination identifiers.
- Immutable Git commit and plugin release identifiers.
- Expected file inventory.
- SHA-256 from raw bytes, or explicitly labeled normalized-text digest.
- Destination readback, not upload success alone.

## Verdicts
MATCH, DRIFTED, MISSING, INCOMPLETE, BLOCKED, UNVERIFIABLE.

## Hard boundaries
Drift is quarantined. No automatic overwrites, deletions, sharing, skill activation, plugin release, merge, deployment, or production writes. Synthetic and metadata-only checks are not byte-level parity proof.
