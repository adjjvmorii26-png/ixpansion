"""Constellation map — render the API module taxonomy as a sky map.

Walks api/ and draws a top-down constellation: every category is a
sector, every module a star. Printed as ASCII from the repo root:

    python tools/constellation_map.py

The map is the machine's face: each module is a named star, and the
gaps between sectors are the dark matter where the next wave will
grow.
"""
from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "api"

SECTOR_ORDER = [
    "core", "revenue", "intelligence", "commerce", "infrastructure",
    "experimental", "meta-evolution", "sensory", "cognitive", "systems",
    "emergence", "integration", "temporal", "social", "metaphysical",
    "cosmic", "consciousness", "transcendence", "existential", "omniscience",
    "recursion", "synthesis", "quantum-aesthetics", "temporal-cartography",
    "biological", "mythogenesis", "entropic-economics", "dimensional",
    "semantic-alchemy", "astral", "workforce", "labor", "civilization",
    "revenue-orchestration", "integrity", "adaptation", "federation",
    "platform", "durable-state", "frontier-cognition", "cognition-ritual",
    "garden", "misc",
]


def scan() -> Counter:
    sectors: Counter = Counter()
    for f in sorted(API.glob("*.py")):
        if f.stem in ("__init__", "index", "unified_router"):
            continue
        sector = f.parent.name if f.parent != API else "core"
        if sector == "core":
            # infer sector from filename conventions
            sector = "core"
        sectors[f"{sector}/{f.stem}"] = 1
    return sectors


def render(width: int = 56) -> str:
    stars = scan()
    # group by sector (first path segment)
    groups: defaultdict = defaultdict(list)
    for key in stars:
        parts = key.split("/")
        sector = parts[0] if len(parts) > 1 else "core"
        name = parts[-1]
        groups[sector].append(name)

    used = {k.split("/")[0] for k in stars}
    sectors = [s for s in SECTOR_ORDER if s in used] + sorted(used - set(SECTOR_ORDER))

    lines = []
    lines.append("IXPANSION — module constellation")
    lines.append("=" * width)
    total = sum(len(v) for v in groups.values())
    lines.append(f"{total} stars in orbit")
    lines.append("")

    for sector in sectors:
        names = groups[sector]
        lines.append(f"· {sector}")
        # 2-column layout
        row = []
        for i, name in enumerate(names):
            row.append(name[:16])
        for i in range(0, len(row), 3):
            lines.append("   " + "   ".join(f"{r:<18}" for r in row[i:i + 3]))
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    print(render())
