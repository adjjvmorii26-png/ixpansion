#!/usr/bin/env python3
"""Recovery Tribunal Dossier — offline human handoff with zero execution authority."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import hashlib
import json
from datetime import datetime, timezone
from html import escape
from typing import Any

from lab.recovery_treaty import verify_treaty
from lab.runtime_vault import (
    CHAIN_FIELDS,
    append_jsonl,
    ledger_path,
    read_json,
    report_path,
    write_json,
)


SCHEMA = "aleph.chronoforge.recovery-dossier.v1"


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(payload: Any) -> str:
    return hashlib.sha256(_canonical(payload)).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _glyph_matrix(seed: str, size: int = 16) -> list[list[int]]:
    material = hashlib.sha256(seed.encode("utf-8")).digest()
    bits = [bool(byte & (1 << bit)) for byte in material for bit in range(7, -1, -1)]
    return [bits[index * size:(index + 1) * size] for index in range(size)]


def _glyph_svg(matrix: list[list[int]]) -> str:
    cells = []
    for row_index, row in enumerate(matrix):
        for column_index, filled in enumerate(row):
            color = "#e2e8f0" if filled else "#0f172a"
            cells.append(
                f'<rect x="{column_index * 12}" y="{row_index * 12}" '
                f'width="11" height="11" fill="{color}"/>'
            )
    return (
        '<svg viewBox="-6 -6 204 204" role="img" '
        'aria-label="Deterministic 16 by 16 witness glyph seal">'
        '<rect x="-5" y="-5" width="202" height="202" fill="#020617" stroke="#38bdf8"/>'
        + "".join(cells) + "</svg>"
    )


def _render(payload: dict[str, Any]) -> str:
    treaty = payload["treaty"]
    packet = treaty["packet"]
    auth = treaty["authorization"]
    signatures = "".join(
        f'<tr><td>{escape(item["role"].replace("_", " ").title())}</td>'
        f'<td>{escape(item["operator_label"])}</td>'
        f'<td><code>{escape(item["key_fingerprint"][:24])}</code></td></tr>'
        for item in auth["signatures"]
    )
    sources = "".join(
        f'<tr><td>{escape(item.get("ledger", "source"))}</td>'
        f'<td><code>{escape(str(item.get("bytes_sha256", "atlas-audit"))[:32])}</code></td>'
        f'<td>{escape(str(item.get("record_count", "sealed")))}</td></tr>'
        for item in treaty["binding"]["sources"]
    )
    checklist = "".join(
        f'<li><span aria-hidden="true">{"✓" if done else "□"}</span> {escape(label)}</li>'
        for label, done in payload["tribunal_checklist"]
    )
    matrix = _glyph_svg(_glyph_matrix(payload["dossier_preview_hash"]))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>ALEPH Recovery Tribunal Dossier</title><style>
:root {{ color-scheme:light dark; --ink:#e2e8f0; --muted:#94a3b8; --panel:#0f172a }} *
{{ box-sizing:border-box }} body {{ margin:0;background:#04070f;color:var(--ink);font-family:ui-sans-serif,system-ui,sans-serif }}
header,main {{ max-width:1080px;margin:auto;padding:28px }} h1,h2,h3 {{ font-family:ui-serif,Georgia,serif;margin:0 }}
.lede,.meta,small {{ color:var(--muted) }} .forbidden {{ border:2px solid #fb7185;color:#fecdd3;padding:14px;border-radius:12px;background:#1f1118 }}
.grid {{ display:grid;grid-template-columns:minmax(260px,340px) 1fr;gap:24px;margin-top:24px }}
.panel {{ background:var(--panel);border:1px solid #223047;border-radius:16px;padding:18px }}
svg {{ width:100%;height:auto }} table {{ width:100%;border-collapse:collapse;margin-top:10px }}
th,td {{ text-align:left;border-bottom:1px solid #223047;padding:8px }} th {{ color:var(--muted);font-weight:500 }}
code {{ color:#7dd3fc;word-break:break-all }} ul {{ padding-left:22px }} li {{ margin:9px 0 }}
footer {{ max-width:1080px;margin:auto;padding:18px 28px 44px;color:var(--muted) }}
@media print {{ body {{ background:white;color:black }} .panel,.forbidden {{ background:white;color:black;border-color:#777 }} }}
</style></head><body>
<header><p class="lede">ALEPH · offline human tribunal</p><h1>Recovery Tribunal Dossier</h1>
<p class="lede">A sealed handoff certificate for one dual-key recovery treaty.</p></header>
<main><div class="forbidden"><strong>Execution is forbidden.</strong>
This dossier contains evidence for deliberation only. No compatible executor exists, and this artifact cannot authorize mutation.</div>
<div class="grid"><section class="panel"><h2>Witness Glyph</h2>{matrix}
<p class="meta"><code>{escape(payload["dossier_preview_hash"])}</code></p></section>
<section class="panel"><h2>Treaty</h2><table><tbody>
<tr><th>Treaty</th><td><code>{escape(treaty["treaty_id"])}</code></td></tr>
<tr><th>Action</th><td>{escape(packet["action"].replace("_", " "))}</td></tr>
<tr><th>Status</th><td>{escape(treaty["status"].replace("_", " "))}</td></tr>
<tr><th>Authority</th><td>{escape(auth["granted_authority"].replace("_", " "))}</td></tr>
<tr><th>Budget</th><td>{auth["live_mutation_budget"]}</td></tr>
</tbody></table></section></div>
<div class="grid" style="margin-top:24px">
<section class="panel"><h2>Signatures</h2><table><thead><tr><th>Office</th><th>Operator</th><th>Fingerprint</th></tr></thead><tbody>{signatures}</tbody></table></section>
<section class="panel"><h2>Bound Sources</h2><table><thead><tr><th>Ledger</th><th>Bytes SHA-256</th><th>Records</th></tr></thead><tbody>{sources}</tbody></table></section>
</div>
<section class="panel" style="max-width:1080px;margin:24px auto 0"><h2>Tribunal Checklist</h2><ul>{checklist}</ul></section>
</main><footer>Dossier <code>{escape(payload["dossier_preview_hash"])}</code> · compiled {escape(payload["compiled_at"])}</footer>
<script>void(0)</script></body></html>"""


def compile_dossier(
    treaty: dict[str, Any],
    *,
    ledgers: list[Path] | None = None,
    key_one: str | None = None,
    key_two: str | None = None,
    max_operations: int | None = None,
    output: Path | None = None,
    record: bool = True,
    clock=utc_now,
) -> dict[str, Any]:
    """Verify a treaty and seal a printable offline tribunal handoff."""
    bound_budget = treaty["binding"].get("lineage_parameters", {}).get(
        "max_operations", 16
    )
    valid_treaty = verify_treaty(
        treaty,
        ledgers=ledgers,
        key_one=key_one,
        key_two=key_two,
        max_operations=max_operations if max_operations is not None else bound_budget,
    )
    if not valid_treaty:
        raise ValueError("recovery treaty is invalid, modified, expired, or unverifiable")

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "experiment": "recovery-tribunal-dossier",
        "status": "sealed",
        "mode": "offline-human-handoff",
        "verdict": "ready_for_tribunal",
        "compiled_at": clock(),
        "treaty": treaty,
        "lineage_parameters": dict(treaty["binding"].get("lineage_parameters", {})),
        "authority": {
            "execution_enabled": False,
            "compatible_executors": [],
            "live_mutation_budget": 0,
            "next_permitted_action": "offline_human_deliberation",
        },
        "tribunal_checklist": [
            ("Confirm both bound source files still match their SHA-256 witnesses", True),
            ("Confirm both treaty signatures were created independently", True),
            ("Confirm the operation remains non-executable", True),
            ("Record the human decision outside this repository", False),
            ("Never permit an executor without a separately reviewed contract", False),
        ],
        "guardrails": [
            "The dossier cannot approve, reject, execute, or mutate.",
            "No executor implementation is included or authorized.",
            "The witness glyph is visual support, not a replacement for hashes.",
        ],
    }
    payload["dossier_preview_hash"] = _hash(payload)[:32]
    payload["html"] = _render(payload)
    payload["dossier_hash"] = _hash(payload)

    if record:
        target = output or report_path("recovery-dossier.html")
        write_json(report_path("recovery-dossier.json"), payload)
        sealed = append_jsonl(
            ledger_path("recovery-dossiers.jsonl"),
            {key: value for key, value in payload.items() if key != "ledger_entry_hash"},
        )
        payload["ledger_entry_hash"] = sealed["entry_hash"]
        write_json(report_path("recovery-dossier.json"), payload)
    elif output:
        target = output
    else:
        return payload

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(payload["html"], encoding="utf-8")
    payload["html_output"] = str(target)
    return payload


def dossier_is_sealed(report: dict[str, Any]) -> bool:
    if report.get("schema") != SCHEMA or report.get("status") != "sealed":
        return False
    claimed = report.get("dossier_hash")
    if not claimed:
        return False
    body = {
        key: value for key, value in report.items()
        if key not in {"dossier_hash", "ledger_entry_hash", "html_output", *CHAIN_FIELDS}
    }
    return _hash(body) == claimed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    compiler = commands.add_parser("compile", help="compile a verified offline dossier")
    compiler.add_argument("--report", type=Path, required=True)
    compiler.add_argument("--output", type=Path, default=None)
    compiler.add_argument("ledgers", nargs="*", type=Path)
    compiler.add_argument("--max-operations", type=int, default=None)
    compiler.add_argument("--no-ledger", action="store_true")
    verifier = commands.add_parser("verify", help="verify a sealed dossier terminal hash")
    verifier.add_argument("--report", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = read_json(args.report, {})
        if args.command == "verify":
            result = {"ok": dossier_is_sealed(report), "dossier_hash": report.get("dossier_hash")}
        else:
            result = compile_dossier(
                report,
                ledgers=args.ledgers or None,
                max_operations=args.max_operations,
                output=args.output,
                record=not args.no_ledger,
            )
            if not args.output and not args.no_ledger:
                pass
            summary = {key: value for key, value in result.items() if key != "html"}
            result = summary
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (OSError, TypeError, ValueError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, sort_keys=True, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
