# Live Notion source-verification adapter

## Purpose
Close the gap where drift only compared **local** snapshots. This adapter compares:

1. Live Notion page body (via injectable fetcher)
2. Pinned `source_sha256` in `provenance.json`
3. Local `seed_snapshot.md`

## Guarantees
- Proposal-only — never writes Notion, never auto-pins, never mutates SKILL.md
- UNAVAILABLE is explicit (not a silent PASS) when fetcher is missing or errors
- Deterministic hashing via same normalize rules as `skill_lab.digest`

## CLI
```bash
# Offline fixture (CI-safe)
python scripts/live_notion_verify.py --export-dir . --fixture /path/to/live_body.txt

# Via skill_lab
python scripts/skill_lab.py live-verify --export-dir . --fixture /path/to/live_body.txt
```

## Wiring a real Notion fetcher
Provide `fetcher(page_id: str) -> str` that returns plain text of the canonical page.

Example (agent / MCP side):
```python
def notion_mcp_fetcher(page_id: str) -> str:
    # call Notion fetch tool; extract plain text body
    ...
    return plain_text
verify_live(Path("."), fetcher=notion_mcp_fetcher)
```

## Finding codes
| Code | Meaning |
|------|---------|
| LIVE_SOURCE_UNAVAILABLE | No fetcher or fetch failed |
| LIVE_SOURCE_DRIFT | Live hash ≠ pinned source_sha256 |
| LIVE_VS_SNAPSHOT_DRIFT | Live hash ≠ local seed_snapshot.md |
| SNAPSHOT_PIN_MISMATCH | Pinned hash ≠ snapshot file hash |
| SOURCE_HASH_UNPINNED | provenance.source_sha256 empty |
| NOTION_PAGE_ID_MISSING | No page id in provenance |
| SNAPSHOT_MISSING | seed_snapshot.md absent |

## Pipeline
`DRIFT_CHECK` remains local. `LIVE_VERIFY` is the new stage (optional until fetcher is wired in CI).

## Status on this branch
- Adapter module + 7 unit tests: green offline
- Live page `40f60373-6996-811b-aa3b-d27b96ca1519` returned 404 from current Notion integration — pin/page access must be confirmed before production LIVE_VERIFY can PASS
