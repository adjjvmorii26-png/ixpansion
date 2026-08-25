#!/usr/bin/env python3
"""Recovery Lineage Atlas — visual audit of the complete recovery chain."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from html import escape
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lab.runtime_vault import (
    CHAIN_FIELDS,
    append_jsonl,
    ledger_path,
    read_json,
    report_path,
    write_json,
)


SCHEMA = "aleph.chronoforge.recovery-lineage-atlas.v1"

STAGE_SPEC = [
    ("paradox", "Paradox Resolve", "recovery-atlas.json", "atlas_hash"),
    ("treaty", "Treaty Compile", "recovery-treaty.json", "treaty_hash"),
    ("dossier", "Dossier Seal", "recovery-dossier.json", "dossier_hash"),
    ("verdict", "Verdict Record", "recovery-verdict.json", "verdict_hash"),
    ("contract", "Executor Contract", "recovery-executor-contract.json", "contract_hash"),
    ("shadow", "Shadow Red Cell", "recovery-shadow-red-cell.json", "red_cell_hash"),
    ("loom", "Manifest Loom", "recovery-manifest-loom.json", "loom_hash"),
    ("crucible", "Answer Crucible", "recovery-answer-crucible.json", "crucible_hash"),
]

STATUS_COLORS = {
    "present": "#22c55e",
    "missing": "#64748b",
    "error": "#ef4444",
}

STAGE_BG = {
    "paradox": "#1e3a5f",
    "treaty": "#2d4a3e",
    "dossier": "#4a3a5f",
    "verdict": "#5f3a3a",
    "contract": "#3a5f5f",
    "shadow": "#4a4a2a",
    "loom": "#3a3a5f",
    "crucible": "#5f4a3a",
}


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(payload: dict[str, Any]) -> str:
    material = {key: value for key, value in payload.items() if key != "atlas_hash"}
    return hashlib.sha256(_canonical(material)).hexdigest()


def _digest_path(stage: str) -> Path:
    return report_path(f"lineage-digest-{stage}.json")


def _scan_stages(runtime_root: Path | None = None) -> list[dict[str, Any]]:
    root = runtime_root or Path(".runtime" if not Path(".runtime").exists() else ".runtime")
    reports_dir = root / "reports"
    results = []
    for key, label, filename, hash_key in STAGE_SPEC:
        path = reports_dir / filename
        report = read_json(path, {})
        if report and isinstance(report, dict) and hash_key in report:
            terminal = str(report.get(hash_key, ""))
            status = "present" if terminal else "error"
        else:
            terminal = ""
            status = "missing"
        results.append({
            "stage": key,
            "label": label,
            "report": filename,
            "hash_key": hash_key,
            "terminal_hash": terminal,
            "status": status,
        })
    return results


def _constellation_svg(stages: list[dict[str, Any]]) -> str:
    center_x, center_y = 500, 220
    radius_x, radius_y = 340, 170
    count = len(stages)
    lines = []
    circles = []
    texts = []
    nodes: list[tuple[float, float]] = []

    for idx, stage in enumerate(stages):
        angle = (2 * math.pi * idx / max(count, 1)) - (math.pi / 2)
        x = center_x + radius_x * math.cos(angle)
        y = center_y + radius_y * math.sin(angle)
        nodes.append((x, y))

    for i, (x, y) in enumerate(nodes):
        next_x, next_y = nodes[(i + 1) % count]
        lines.append(
            f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{next_x:.1f}" y2="{next_y:.1f}" '
            'stroke="#475569" stroke-width="2" stroke-opacity="0.6"/>'
        )

    for i, (stage, (x, y)) in enumerate(zip(stages, nodes)):
        color = STATUS_COLORS[stage["status"]]
        bg = STAGE_BG.get(stage["stage"], "#1e293b")
        r = 28
        lines.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{bg}" stroke="{color}" stroke-width="3"/>'
        )
        label = escape(stage["label"])
        lines.append(f'<text x="{x:.1f}" y="{y - 6:.1f}" text-anchor="middle" class="stage">{label}</text>')
        if stage["terminal_hash"]:
            short = escape(stage["terminal_hash"][:12])
            lines.append(f'<text x="{x:.1f}" y="{y + 12:.1f}" text-anchor="middle" class="hash">{short}</text>')
        else:
            lines.append(f'<text x="{x:.1f}" y="{y + 12:.1f}" text-anchor="middle" class="hash dim">absent</text>')

    lines.append(f'<circle cx="{center_x}" cy="{center_y}" r="36" fill="#0f172a" stroke="#38bdf8" stroke-width="3"/>')
    lines.append(f'<text x="{center_x}" y="{center_y - 4}" text-anchor="middle" class="center">LINEAGE</text>')
    lines.append(f'<text x="{center_x}" y="{center_y + 14}" text-anchor="middle" class="center-sub">ATLAS</text>')

    return "\n".join(lines)


def _render(payload: dict[str, Any]) -> str:
    stages = payload["stages"]
    present = sum(1 for s in stages if s["status"] == "present")
    total = len(stages)
    svg = _constellation_svg(stages)
    rows = "".join(
        f'<tr><td>{escape(s["label"])}</td><td class="{s["status"]}">{escape(s["status"])}</td>'
        f'<td class="mono">{escape(s["terminal_hash"][:20] if s["terminal_hash"] else "—")}</td></tr>'
        for s in stages
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ALEPH Recovery Lineage Atlas</title>
<style>
body {{ font-family: system-ui, -apple-system, sans-serif; background: #0a0f1a; color: #e2e8f0; margin: 0; padding: 24px; }}
.atlas {{ max-width: 1100px; margin: 0 auto; }}
header {{ text-align: center; margin-bottom: 32px; }}
h1 {{ font-size: 1.6rem; margin: 0 0 8px; }}
.lead {{ color: #94a3b8; }}
svg {{ display: block; margin: 0 auto 32px; }}
.center {{ fill: #38bdf8; font-weight: 700; font-size: 11px; }}
.center-sub {{ fill: #94a3b8; font-size: 9px; }}
.stage {{ fill: #e2e8f0; font-size: 11px; font-weight: 600; }}
.hash {{ fill: #94a3b8; font-size: 9px; }}
.hash.dim {{ fill: #64748b; }}
table {{ width: 100%; border-collapse: collapse; }}
th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid #1e293b; }}
th {{ color: #94a3b8; font-size: 0.85rem; }}
.present {{ color: #22c55e; }}
.missing {{ color: #64748b; }}
.error {{ color: #ef4444; }}
.mono {{ font-family: ui-monospace, monospace; font-size: 0.8rem; color: #94a3b8; }}
footer {{ text-align: center; color: #64748b; margin-top: 24px; font-size: 0.85rem; }}
</style></head><body>
<div class="atlas">
<header><h1>ALEPH Recovery Lineage Atlas</h1><p class="lead">{present} of {total} stages present · sealed audit constellation</p></header>
<svg viewBox="0 0 1000 440" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:900px;height:auto;">{svg}</svg>
<table><thead><tr><th>Stage</th><th>Status</th><th>Terminal Hash</th></tr></thead><tbody>{rows}</tbody></table>
<footer>Atlas hash: {escape(payload.get("atlas_hash", "")[:24])} · sealed {escape(payload.get("sealed_at", ""))}</footer>
</div></body></html>"""


def compile_lineage_atlas(
    *,
    runtime_root: Path | None = None,
    record: bool = True,
    output: Path | None = None,
    clock=__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat,
) -> dict[str, Any]:
    """Read recovery reports and produce one sealed lineage observatory."""
    stages = _scan_stages(runtime_root)
    stage_hashes = {s["stage"]: s["terminal_hash"] for s in stages}
    present_count = sum(1 for s in stages if s["status"] == "present")
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "experiment": "recovery-lineage-atlas",
        "status": "sealed",
        "mode": "read-only-audit",
        "stage_count": len(stages),
        "stages": stages,
        "stage_hashes": stage_hashes,
        "present_stages": present_count,
        "seal_seed": {
            "stage_hashes": stage_hashes,
            "present_count": present_count,
        },
    }
    result["execution_enabled"] = False
    result["sealed_at"] = clock() if callable(clock) else str(clock)
    result["atlas_hash"] = _hash(result)
    result["html"] = _render(result)

    if record:
        write_json(report_path("recovery-lineage-atlas.json"), result)
        sealed = append_jsonl(
            ledger_path("recovery-lineage-atlases.jsonl"),
            {key: value for key, value in result.items() if key not in {"ledger_entry_hash", "html"}},
        )
        result["ledger_entry_hash"] = sealed["entry_hash"]
        write_json(report_path("recovery-lineage-atlas.json"), result)
    elif output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(result["html"], encoding="utf-8")
        result["html_output"] = str(output)
    return result


def atlas_is_sealed(report: dict[str, Any]) -> bool:
    if report.get("schema") != SCHEMA or report.get("status") != "sealed":
        return False
    claimed = report.get("atlas_hash")
    if not claimed:
        return False
    body = {
        key: value for key, value in report.items()
        if key not in {"atlas_hash", "ledger_entry_hash", "html", *CHAIN_FIELDS}
    }
    return _hash(body) == claimed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-root", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--stdout", action="store_true")
    parser.add_argument("--no-ledger", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = compile_lineage_atlas(
            runtime_root=args.runtime_root,
            record=not args.no_ledger,
            output=args.output,
        )
        if args.stdout:
            import sys
            sys.stdout.write(result["html"])
            sys.stdout.write("\n")
        elif not args.output:
            print(json.dumps({
                "schema": result["schema"],
                "atlas_hash": result["atlas_hash"],
                "present_stages": result["present_stages"],
                "stage_count": result["stage_count"],
            }, indent=2))
        return 0
    except (OSError, TypeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
