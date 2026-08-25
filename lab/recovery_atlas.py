#!/usr/bin/env python3
"""Recovery Atlas — compile the paradox-to-consent journey into one sealed observatory."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import hashlib
import json
import math
from html import escape
from typing import Any

from lab.recovery_quorum import convene
from lab.repair_dreams import weave
from lab.repair_theater import rehearse
from lab.runtime_vault import (
    CHAIN_FIELDS,
    append_jsonl,
    ledger_path,
    read_jsonl,
    report_path,
    verify_jsonl,
    write_json,
)
from lab.temporal_paradox import resolve


SCHEMA = "aleph.chronoforge.recovery-atlas.v1"
DERIVED_LEDGERS = {
    "paradox-resolutions.jsonl",
    "repair-dreams.jsonl",
    "repair-theater.jsonl",
    "recovery-quorums.jsonl",
    "recovery-atlases.jsonl",
}
STATUS_COLORS = {
    "staged": "#38bdf8",
    "retained": "#a78bfa",
    "quarantined": "#fb7185",
    "refused": "#f97316",
}


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(payload: Any) -> str:
    return hashlib.sha256(_canonical(payload)).hexdigest()


def _source_paths(explicit: list[Path] | None) -> list[Path]:
    if explicit is None:
        directory = ledger_path().parent
        return sorted(path for path in directory.glob("*.jsonl") if path.name not in DERIVED_LEDGERS)
    paths = sorted({Path(item).resolve() for item in explicit})
    for item in paths:
        if not item.is_file():
            raise ValueError(f"ledger does not exist: {item}")
    return paths


def _audit_paths(paths: list[Path]) -> dict[str, dict[str, Any]]:
    return {path.name: verify_jsonl(path) for path in paths}


def _upstream(paths: list[Path], max_operations: int) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    diagnosis = resolve(ledgers=paths, record=False)
    dream = weave(ledgers=paths, max_operations=max_operations, record=False)
    theater = rehearse(ledgers=paths, max_operations=max_operations, record=False)
    quorum = convene(ledgers=paths, max_operations=max_operations, record=False)
    return diagnosis, dream, theater, quorum


def _scene_card(scene: dict[str, Any]) -> str:
    offices = " · ".join(
        f"<strong>{escape(name.title())}</strong> {escape(vote)}"
        for name, vote in scene.get("offices", {}).items()
    )
    risks = "".join(f"<small>{escape(risk)}</small>" for risk in scene.get("residual_risks", []))
    recommendation = escape(str(scene.get("recommendation", "unreviewed")).replace("_", " "))
    action = escape(str(scene.get("action", "")).replace("_", " "))
    status = escape(str(scene.get("status", "")))
    kind = escape(str(scene.get("kind", "unknown")).replace("_", " "))
    branches = len(scene.get("branches", []))
    stability = scene.get("stability", 0)
    return f"""<article class="scene">
<header><span class=\\"dot\\"></span><h3>{kind}</h3></header>
<p>{action} · {status}</p>
<p class=\\"meta\\">branches {branches} · stability {stability} · {recommendation}</p>
<p>{offices}</p>
{risks}
</article>"""


def _constellation(scenes: list[dict[str, Any]]) -> str:
    center_x, center_y = 480, 260
    parts = [
        f'<circle cx="{center_x}" cy="{center_y}" r="42" fill="#0f172a" stroke="#38bdf8"/>',
        f'<text x="{center_x}" y="{center_y + 4}">ALEPH</text>',
    ]
    count = len(scenes)
    for index, scene in enumerate(scenes):
        angle = (2 * math.pi * index / max(count, 1)) - (math.pi / 2)
        x = center_x + 330 * math.cos(angle)
        y = center_y + 180 * math.sin(angle)
        color = STATUS_COLORS.get(str(scene.get("status")), "#94a3b8")
        parts.append(
            f'<line x1="{center_x}" y1="{center_y}" x2="{x:.1f}" y2="{y:.1f}" '
            'stroke="#334155" stroke-width="2" stroke-opacity=".75"/>'
        )
        parts.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="17" fill="#020617" '
            f'stroke="{color}" stroke-width="3"/>'
        )
        label = escape(str(scene.get("kind", "")).replace("_", " "))
        parts.append(f'<text x="{x:.1f}" y="{y + 36:.1f}" class="meta">{label}</text>')
        parts.append(f'<text x="{x:.1f}" y="{y + 50:.1f}" class="meta">stability {scene.get("stability", 0)}</text>')
    return "".join(parts)


def _render(payload: dict[str, Any]) -> str:
    upstream = payload["upstream"]
    scenes = payload["journey"]["quorum"]["scenes"]
    packets = payload["journey"]["quorum"]["consent_packets"]
    chips = "".join(
        f'<span class="chip"><b>{escape(name.replace("_", " ").title())}</b> '
        f'{escape(item["verdict"])}<code>{escape(item["hash"][:16])}</code></span>'
        for name, item in upstream.items()
    )
    cards = "".join(_scene_card(scene) for scene in scenes)
    packet_items = "".join(
        f'<li><strong>{escape(item["operation_id"])}</strong>'
        '<small>two human signatures required · '
        f'executable {item["executable"]} · budget {item["mutation_budget"]}</small></li>'
        for item in packets
    ) or "<li>No consent packet is currently ready.</li>"
    preview = payload["atlas_preview_hash"]
    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>ALEPH Recovery Atlas</title><style>
:root {{ color-scheme:dark; --ink:#e2e8f0; --muted:#94a3b8; --panel:#0f172a }} *
{{ box-sizing:border-box }} body {{ margin:0;background:#04070f;color:var(--ink);font-family:ui-sans-serif,system-ui,sans-serif }}
header,main {{ max-width:1180px;margin:auto;padding:28px }} h1,h2,h3 {{ font-family:ui-serif,Georgia,serif;margin:0 }}
.lede,.meta,small {{ color:var(--muted) }} .chips {{ display:flex;flex-wrap:wrap;gap:10px;margin-top:18px }}
.chip {{ border:1px solid #223047;border-radius:999px;padding:7px 12px;background:#0b1120;font-size:13px }}
.chip code {{ margin-left:8px;color:#7dd3fc }} svg {{ width:100%;height:auto }}
.map {{ background:#080d19;border:1px solid #1e293b;border-radius:18px;padding:16px;margin-bottom:24px }}
circle {{ stroke-width:2 }} text {{ fill:#e2e8f0;text-anchor:middle;font-size:13px }} .meta {{ font-size:9px;fill:#94a3b8 }}
.grid {{ display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:16px }}
.scene,.packets {{ background:var(--panel);border:1px solid #223047;border-radius:15px;padding:16px }}
.scene header {{ display:flex;align-items:center;gap:9px;padding:0 }} .dot {{ width:11px;height:11px;border-radius:50%;background:#38bdf8 }}
.scene p {{ margin:8px 0 }} .scene .meta,small {{ font-size:12px;display:block }}
.packets li {{ margin:12px 0 }} footer {{ max-width:1180px;margin:auto;padding:20px 28px 44px;color:var(--muted) }}
</style></head><body>
<header><p class="lede">ALEPH · Chrono Forge recovery intelligence</p><h1>Recovery Atlas</h1>
<p class="lede">A sealed, zero-authority map from paradox evidence to ghost rehearsal to human consent.</p>
<div class="chips">{chips}</div></header>
<main><section class="map"><svg viewBox="0 0 960 520" role="img" aria-label="Radial recovery constellation">{_constellation(scenes)}</svg></section>
<section class="grid">{cards}</section>
<section class="packets" style="margin-top:24px"><h2>Consent Packets</h2><ul>{packet_items}</ul></section>
</main><footer>Atlas <code>{preview}</code> · execution forbidden</footer>
<script>void(0)</script></body></html>"""


def compile_atlas(
    *,
    ledgers: list[Path] | None = None,
    max_operations: int = 16,
    output: Path | None = None,
    record: bool = True,
) -> dict[str, Any]:
    """Run every recovery stage read-only and seal one navigable atlas."""
    if not 1 <= max_operations <= 32:
        raise ValueError("max-operations must be between 1 and 32")
    paths = _source_paths(ledgers)
    if not paths:
        raise ValueError("no source ledgers are available for the atlas")
    audits = _audit_paths(paths)
    diagnosis, dream, theater, quorum = _upstream(paths, max_operations)
    record_counts = {path.name: len(read_jsonl(path)) for path in paths}
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "experiment": "recovery-atlas",
        "status": "sealed",
        "mode": "read-only",
        "verdict": quorum["verdict"],
        "source_audits_ok": all(item["ok"] for item in audits.values()),
        "sources": {
            "ledger_count": len(paths),
            "records": record_counts,
            "audits": audits,
        },
        "upstream": {
            "paradox": {"hash": diagnosis["paradox_hash"], "verdict": diagnosis["verdict"], "count": diagnosis["paradox_count"]},
            "dreams": {"hash": dream["dream_hash"], "verdict": dream["verdict"], "count": dream["operation_count"]},
            "theater": {"hash": theater["theater_hash"], "verdict": theater["verdict"], "count": theater["stage_count"]},
            "quorum": {"hash": quorum["quorum_hash"], "verdict": quorum["verdict"], "count": quorum["consent_packet_count"]},
        },
        "journey": {"diagnosis": diagnosis, "dream": dream, "theater": theater, "quorum": quorum},
        "execution_enabled": False,
        "live_mutation_budget": 0,
        "guardrails": [
            "The atlas renders evidence; it never executes repairs.",
            "All stages receive identical immutable source paths.",
            "Consent packets require separate human signatures.",
        ],
    }
    payload["atlas_preview_hash"] = _hash(payload)[:32]
    payload["html"] = _render(payload)
    payload["atlas_hash"] = _hash(payload)

    if record:
        target = output or report_path("recovery-atlas.html")
        write_json(report_path("recovery-atlas.json"), payload)
        sealed = append_jsonl(
            ledger_path("recovery-atlases.jsonl"),
            {key: value for key, value in payload.items() if key != "ledger_entry_hash"},
        )
        payload["ledger_entry_hash"] = sealed["entry_hash"]
        write_json(report_path("recovery-atlas.json"), payload)
    elif output:
        target = output
    else:
        return payload

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(payload["html"], encoding="utf-8")
    payload["html_output"] = str(target)
    return payload


def atlas_is_sealed(report: dict[str, Any]) -> bool:
    if report.get("schema") != SCHEMA or report.get("status") != "sealed":
        return False
    claimed = report.get("atlas_hash")
    if not claimed:
        return False
    body = {
        key: value for key, value in report.items()
        if key not in {"atlas_hash", "ledger_entry_hash", "html_output", *CHAIN_FIELDS}
    }
    return _hash(body) == claimed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledgers", nargs="*", type=Path)
    parser.add_argument("--max-operations", type=int, default=16)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--stdout", action="store_true", help="print HTML instead of a JSON summary")
    parser.add_argument("--no-ledger", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = compile_atlas(
            ledgers=args.ledgers or None,
            max_operations=args.max_operations,
            output=args.output,
            record=not args.no_ledger,
        )
        if args.stdout:
            print(result["html"])
        else:
            summary = {key: value for key, value in result.items() if key not in {"html", "journey"}}
            print(json.dumps(summary, sort_keys=True, indent=2))
        return 0
    except (OSError, TypeError, ValueError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, sort_keys=True, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
