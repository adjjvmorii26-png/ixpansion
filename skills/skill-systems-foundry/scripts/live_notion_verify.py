"""Live Notion source-verification adapter.

Compares canonical Notion page content against:
  - pinned source_sha256 in provenance.json
  - local seed_snapshot.md

Proposal-only. Never writes to Notion or mutates source.
Fetcher is injectable so CI can run offline with fixtures.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional


def normalize(text: str) -> str:
    """Canonical text normalization for hashing (matches skill_lab.digest)."""
    return text.replace("\r\n", "\n")


def digest(text: str) -> str:
    return hashlib.sha256(normalize(text).encode("utf-8")).hexdigest()


def strip_notion_noise(text: str) -> str:
    """Light cleanup for Notion export text before hash.

    Keeps semantic content; drops common export chrome that varies by client.
    Does not invent content.
    """
    t = normalize(text)
    # collapse runs of blank lines
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip() + ("\n" if t.strip() else "")


Fetcher = Callable[[str], str]  # page_id -> plain text body


@dataclass
class LiveVerifyResult:
    status: str  # PASS | DRIFT | UNAVAILABLE | UNPINNED | ERROR
    findings: list = field(default_factory=list)
    live_sha256: Optional[str] = None
    snapshot_sha256: Optional[str] = None
    pinned_source_sha256: Optional[str] = None
    notion_page_id: Optional[str] = None
    scope: str = "live Notion source verification (not auto-repair)"

    def to_dict(self):
        return {
            "status": self.status,
            "findings": self.findings,
            "live_sha256": self.live_sha256,
            "snapshot_sha256": self.snapshot_sha256,
            "pinned_source_sha256": self.pinned_source_sha256,
            "notion_page_id": self.notion_page_id,
            "scope": self.scope,
            "automatic_changes": False,
            "repair_mode": "PROPOSAL_ONLY",
        }


def load_provenance(folder: Path) -> dict:
    path = folder / "provenance.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def verify_live(
    folder: Path,
    fetcher: Optional[Fetcher] = None,
    page_id: Optional[str] = None,
) -> LiveVerifyResult:
    """Verify live Notion source against snapshot and pinned hashes.

    fetcher(page_id) must return the plain-text body of the canonical page.
    If fetcher is None or raises, status is UNAVAILABLE (not a silent pass).
    """
    meta = load_provenance(folder)
    pid = page_id or meta.get("notion_page_id") or ""
    pinned = meta.get("source_sha256") or ""
    result = LiveVerifyResult(status="PASS", notion_page_id=pid or None, pinned_source_sha256=pinned or None)

    snapshot_path = folder / (meta.get("source_snapshot") or "seed_snapshot.md")
    if snapshot_path.exists():
        snap_text = snapshot_path.read_text(encoding="utf-8")
        result.snapshot_sha256 = digest(snap_text)
    else:
        result.findings.append({"code": "SNAPSHOT_MISSING", "path": str(snapshot_path)})

    if not pid:
        result.findings.append({"code": "NOTION_PAGE_ID_MISSING"})
        result.status = "ERROR"
        return result

    if not pinned:
        result.findings.append({"code": "SOURCE_HASH_UNPINNED"})

    if fetcher is None:
        result.findings.append({
            "code": "LIVE_SOURCE_UNAVAILABLE",
            "reason": "no fetcher provided (wire Notion MCP / API client)",
        })
        result.status = "UNAVAILABLE"
        return result

    try:
        live_raw = fetcher(pid)
    except Exception as exc:  # intentional: adapter must not crash pipeline
        result.findings.append({
            "code": "LIVE_SOURCE_UNAVAILABLE",
            "reason": str(exc)[:240],
        })
        result.status = "UNAVAILABLE"
        return result

    live_norm = strip_notion_noise(live_raw)
    result.live_sha256 = digest(live_norm)

    if pinned and result.live_sha256 != pinned:
        result.findings.append({
            "code": "LIVE_SOURCE_DRIFT",
            "expected": pinned,
            "actual": result.live_sha256,
            "diagnosis": "Live Notion body differs from pinned source_sha256.",
            "repair_proposal": "Inspect live page vs seed; update pin only after human review. Never auto-overwrite Notion.",
        })
        result.status = "DRIFT"

    if result.snapshot_sha256 and result.live_sha256 != result.snapshot_sha256:
        result.findings.append({
            "code": "LIVE_VS_SNAPSHOT_DRIFT",
            "expected": result.snapshot_sha256,
            "actual": result.live_sha256,
            "diagnosis": "Live Notion body differs from local seed_snapshot.md.",
            "repair_proposal": "Refresh seed_snapshot.md from live read-back after review, or restore Notion to snapshot.",
        })
        if result.status == "PASS":
            result.status = "DRIFT"

    if pinned and result.snapshot_sha256 and pinned != result.snapshot_sha256:
        result.findings.append({
            "code": "SNAPSHOT_PIN_MISMATCH",
            "pinned": pinned,
            "snapshot": result.snapshot_sha256,
            "diagnosis": "Local snapshot hash does not match pinned source_sha256.",
            "repair_proposal": "Re-pin after intentional snapshot update; do not silently rewrite.",
        })
        if result.status == "PASS":
            result.status = "DRIFT"

    if result.findings and result.status == "PASS":
        # e.g. only UNPINNED warning
        if any(f.get("code") == "SOURCE_HASH_UNPINNED" for f in result.findings):
            result.status = "UNPINNED"

    return result


def pin_from_text(text: str) -> str:
    """Compute pin hash for a reviewed snapshot (human-triggered only)."""
    return digest(strip_notion_noise(text))


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Live Notion source verification (proposal-only)")
    ap.add_argument("--export-dir", required=True, help="Folder with provenance.json + seed_snapshot.md")
    ap.add_argument("--page-id", help="Override notion_page_id from provenance")
    ap.add_argument("--fixture", help="Offline fixture file used as live body (no network)")
    args = ap.parse_args()
    folder = Path(args.export_dir)

    fetcher = None
    if args.fixture:
        body = Path(args.fixture).read_text(encoding="utf-8")
        fetcher = lambda _pid, b=body: b

    result = verify_live(folder, fetcher=fetcher, page_id=args.page_id)
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
