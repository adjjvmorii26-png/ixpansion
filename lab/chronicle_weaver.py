#!/usr/bin/env python3
"""Chronicle Weaver — readable HTML timeline from hash-chained ledger events."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lab.runtime_vault import (
    CHAIN_FIELDS,
    ledger_path,
    read_json,
    read_jsonl,
    verify_jsonl,
    write_json,
    state_path,
)

SCHEMA = "aleph.experiments.chronicle-weaver.v1"
TYPE_LABELS = {
    "sandbox_ticks": "Sandbox Ticks",
    "swarm_sandbox_cycle": "Swarm Pulse",
    "entropy_cartograph": "Entropy Cartograph",
    "pulse": "Pulse Oracle",
    "quorum": "Recovery Quorum",
    "echo": "Ancestral Echo",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(payload: dict[str, Any]) -> str:
    material = {k: v for k, v in payload.items() if k != "weave_hash"}
    return hashlib.sha256(_canonical(material)).hexdigest()


def _html_text(value: Any) -> str:
    """Encode untrusted values for an HTML text-node context."""
    return html.escape("" if value is None else str(value), quote=True)


def _label_for(entry_type: str) -> str:
    return TYPE_LABELS.get(entry_type, entry_type.replace("_", " ").title())


def _entry_summary(entry: dict[str, Any]) -> str:
    parts = []
    if "total_ticks" in entry:
        parts.append(f"{entry['total_ticks']} ticks completed")
    if "ticks" in entry and "total_ticks" not in entry:
        parts.append(f"{entry['ticks']} ticks")
    if "observations" in entry:
        parts.append(f"{entry['observations']} observations")
    if "dominant" in entry:
        parts.append(f"dominant: {entry['dominant']}")
    if "coherence" in entry:
        parts.append(f"coherence: {entry['coherence']}")
    return ", ".join(parts) if parts else "sealed event"


def _weave_chronicle(entries: list[dict[str, Any]], *, clock: Any = utc_now) -> dict[str, Any]:
    type_groups: dict[str, list[dict[str, Any]]] = {}
    for entry in entries:
        t = entry.get("type", "unknown")
        type_groups.setdefault(t, []).append(entry)
    timeline_items = []
    for entry in entries:
        entry_type = entry.get("type", "unknown")
        timeline_items.append({
            "timestamp": entry.get("ts", ""),
            "type": entry_type,
            "label": _label_for(entry_type),
            "ref": entry.get("ref", ""),
            "summary": _entry_summary(entry),
            "sequence": entry.get("sequence"),
        })
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "experiment": "chronicle-weaver",
        "status": "sealed",
        "mode": "read-only-narrative",
        "sealed_at": clock(),
        "total_entries": len(entries),
        "type_summary": {t: len(items) for t, items in type_groups.items()},
        "unique_types": len(type_groups),
        "timeline": timeline_items,
        "execution_enabled": False,
    }
    result["weave_hash"] = _hash(result)
    return result


def _render(payload: dict[str, Any]) -> str:
    summary_rows = "".join(
        f'<tr><td>{_html_text(str(t).replace("_", " ").title())}</td><td>{_html_text(c)}</td></tr>'
        for t, c in payload.get("type_summary", {}).items()
    )
    timeline = "".join(
        f'<li><span class="ts">{_html_text(item.get("timestamp", ""))}</span> '
        f'<span class="tag">{_html_text(item.get("label", ""))}</span> '
        f'<span class="ref">{_html_text(str(item.get("ref") or "")[:16] or "—")}</span> '
        f'<span class="summary">{_html_text(item.get("summary", ""))}</span></li>'
        for item in payload.get("timeline", [])
    )
    audit = payload.get("audit", {})
    warning = ""
    if not audit.get("ok", False):
        failure = audit.get("failure") or {}
        warning = (
            '<aside role="alert" class="warning">'
            '<strong>UNTRUSTED LEDGER — integrity verification failed.</strong> '
            f'Records below are diagnostic only. Failure: {_html_text(failure.get("kind", "unknown"))}. '
            'Do not use this report as verified evidence.</aside>'
        )
    status = _html_text(payload.get("status", "unknown"))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Chronicle — {status}</title>
<style>
body {{ font-family: system-ui, sans-serif; background: #0a0f1a; color: #e2e8f0; margin: 0; padding: 24px; }}
.wrap {{ max-width: 800px; margin: 0 auto; }}
h1 {{ font-size: 1.4rem; }}
table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; margin-bottom: 24px; }}
th, td {{ padding: 6px 10px; border-bottom: 1px solid #1e293b; text-align: left; }}
th {{ color: #94a3b8; }}
ul {{ list-style: none; padding: 0; }}
li {{ padding: 10px 0; border-bottom: 1px solid #1e293b; font-size: 0.9rem; }}
.ts {{ color: #64748b; font-size: 0.8rem; }}
.tag {{ color: #38bdf8; font-weight: 600; }}
.ref {{ color: #94a3b8; font-family: ui-monospace, monospace; font-size: 0.8rem; }}
.summary {{ color: #cbd5e1; }}
.warning {{ border: 2px solid #f87171; background: #451a1a; padding: 12px; margin: 16px 0; }}
footer {{ color: #64748b; font-size: 0.8rem; margin-top: 16px; }}
</style></head><body><div class="wrap">
<h1>Chronicle</h1>
{warning}
<p>{_html_text(payload.get("total_entries", 0))} entries · {_html_text(payload.get("unique_types", 0))} unique types · sealed {_html_text(payload.get("sealed_at", ""))}</p>
<table><thead><tr><th>Type</th><th>Count</th></tr></thead><tbody>{summary_rows}</tbody></table>
<ul>{timeline}</ul>
<footer>status {_html_text(status)} · hash {_html_text(str(payload.get("weave_hash", ""))[:20])}</footer>
</div></body></html>"""


def weave_chronicle(
    *,
    ledger_name: str = "proof.jsonl",
    record: bool = True,
    clock: Any = utc_now,
    output: Path | None = None,
) -> dict[str, Any]:
    """Read the proof ledger and weave a readable HTML chronicle."""
    path = ledger_path(ledger_name)
    audit = verify_jsonl(path)
    entries = read_jsonl(path)
    result = _weave_chronicle(entries, clock=clock)
    result["audit"] = {"ok": audit["ok"], "records": audit["records"], "failure": audit.get("failure")}
    result["status"] = "sealed" if audit["ok"] else "untrusted"
    # Keep the report digest aligned with the rendered status while preserving
    # the established contract that the audit envelope itself is not hashed.
    result["weave_hash"] = _hash({k: v for k, v in result.items() if k != "audit"})
    result["html"] = _render(result)

    if record:
        write_json(state_path("chronicle", "latest.json"), {k: v for k, v in result.items() if k != "html"})
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(result["html"], encoding="utf-8")
        result["html_output"] = str(output)
    return result


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ledger", default="proof.jsonl")
    p.add_argument("--output", type=Path, default=None)
    p.add_argument("--no-ledger", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = weave_chronicle(
            ledger_name=args.ledger,
            record=not args.no_ledger,
            output=args.output,
        )
        if args.output:
            print(json.dumps({"html_output": result.get("html_output"), "weave_hash": result["weave_hash"]}, indent=2))
        else:
            sys.stdout.write(result["html"])
            sys.stdout.write("\n")
        return 0
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
