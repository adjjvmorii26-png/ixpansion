#!/usr/bin/env python3
"""Entropy Cartographer — sandbox tick heat-map observatory."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lab.runtime_vault import (
    CHAIN_FIELDS,
    append_jsonl,
    ledger_path,
    state_path,
    write_json,
)
from sandbox.sandbox_engine import run_ticks


SCHEMA = "aleph.experiments.entropy-cartographer.v1"
COLS = 10


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(payload: dict[str, Any]) -> str:
    material = {k: v for k, v in payload.items() if k != "cartograph_hash"}
    return hashlib.sha256(_canonical(material)).hexdigest()


def _energy_color(energy: float) -> str:
    h = max(0.0, min(1.0, energy))
    r = int(30 + 180 * h)
    g = int(40 + 60 * (1 - abs(h - 0.5) * 2))
    b = int(80 + 120 * (1 - h))
    return f"#{r:02x}{g:02x}{b:02x}"


def _heat_svg(cells: list[dict[str, Any]], cols: int) -> str:
    rows = math.ceil(len(cells) / cols) if cells else 1
    cell_w, cell_h = 48, 36
    pad = 4
    total_w = cols * (cell_w + pad) + pad
    total_h = rows * (cell_h + pad) + pad
    parts = []
    for i, cell in enumerate(cells):
        x = pad + (i % cols) * (cell_w + pad)
        y = pad + (i // cols) * (cell_h + pad)
        color = _energy_color(cell["energy"])
        parts.append(
            f'<rect x="{x}" y="{y}" width="{cell_w}" height="{cell_h}" rx="4" fill="{color}"/>'
        )
        parts.append(
            f'<text x="{x + cell_w // 2}" y="{y + 14}" text-anchor="middle" class="cell-label">T{cell["tick"]}</text>'
        )
        parts.append(
            f'<text x="{x + cell_w // 2}" y="{y + 26}" text-anchor="middle" class="cell-val">{cell["energy"]:.2f}</text>'
        )
    return (
        f'<svg viewBox="0 0 {total_w} {total_h}" xmlns="http://www.w3.org/2000/svg" '
        f'style="width:100%;max-width:{total_w}px;height:auto;">'
        f'<style>.cell-label {{font-size:9px;fill:#cbd5e1;}} .cell-val {{font-size:8px;fill:#94a3b8;}}</style>'
        f'{" ".join(parts)}</svg>'
    )


def _render(payload: dict[str, Any]) -> str:
    cells = payload["cells"]
    svg = _heat_svg(cells, COLS)
    rows = "".join(
        f'<tr><td>T{c["tick"]}</td><td style="color:{_energy_color(c["energy"])}">{c["energy"]:.3f}</td>'
        f'<td>{c["phase"]:.2f}</td><td>{c["novelty"]:.3f}</td></tr>'
        for c in cells
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Entropy Cartograph</title>
<style>
body {{ font-family: system-ui, sans-serif; background: #0a0f1a; color: #e2e8f0; margin: 0; padding: 24px; }}
.wrap {{ max-width: 900px; margin: 0 auto; }}
h1 {{ font-size: 1.4rem; }}
svg {{ margin: 16px 0; }}
table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
th, td {{ padding: 6px 10px; border-bottom: 1px solid #1e293b; }}
th {{ color: #94a3b8; }}
.mono {{ font-family: ui-monospace, monospace; color: #94a3b8; font-size: 0.8rem; }}
footer {{ color: #64748b; font-size: 0.8rem; margin-top: 16px; }}
</style></head><body><div class="wrap">
<h1>Entropy Cartograph</h1>
<p>{payload["tick_count"]} ticks · budget {payload["entropy_budget_end"]:.3f} · novelty range {payload["novelty_min"]:.3f}–{payload["novelty_max"]:.3f}</p>
{svg}
<table><thead><tr><th>Tick</th><th>Energy</th><th>Phase</th><th>Novelty</th></tr></thead><tbody>{rows}</tbody></table>
<footer>hash {payload["cartograph_hash"][:20]} · sealed {payload["sealed_at"]}</footer>
</div></body></html>"""


def cartograph(
    *,
    ticks: int = 20,
    record: bool = True,
    clock: Any = utc_now,
) -> dict[str, Any]:
    """Run sandbox ticks and render an entropy heat-map."""
    if not 1 <= ticks <= 200:
        raise ValueError("ticks must be between 1 and 200")
    sandbox = run_ticks(ticks, proof=False)
    history = list(sandbox.get("history", [])[-ticks:])
    cells = [
        {"tick": h["tick"], "energy": h["energy"], "phase": h.get("a", 0), "novelty": abs(h.get("a", 0) - h.get("b", 0))}
        for h in history
    ]
    energies = [c["energy"] for c in cells] if cells else [0]
    novelties = [c["novelty"] for c in cells] if cells else [0]
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "experiment": "entropy-cartographer",
        "status": "sealed",
        "mode": "read-only-visualization",
        "sealed_at": clock(),
        "tick_count": len(cells),
        "entropy_budget_end": sandbox.get("entropy_budget", 0),
        "energy_mean": round(sum(energies) / max(1, len(energies)), 4),
        "energy_max": round(max(energies), 4),
        "novelty_min": round(min(novelties), 4),
        "novelty_max": round(max(novelties), 4),
        "cells": cells,
        "execution_enabled": False,
    }
    result["cartograph_hash"] = _hash(result)
    result["html"] = _render(result)

    if record:
        write_json(state_path("cartographer", "latest.json"), {k: v for k, v in result.items() if k != "html"})
        append_jsonl(
            ledger_path(),
            {"type": "entropy_cartograph", "ref": result["cartograph_hash"], "ticks": len(cells)},
        )
    return result


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ticks", type=int, default=20)
    p.add_argument("--no-ledger", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = cartograph(ticks=args.ticks, record=not args.no_ledger)
        import sys
        sys.stdout.write(result["html"])
        sys.stdout.write("\n")
        return 0
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
