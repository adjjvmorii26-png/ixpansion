"""Consciousness Meter — measures the frontier's awareness across dimensions.

The meter computes a composite score (0-100) from five axes:
  - INTEGRITY   — tests, modules, routes (the body)
  - CREATIVITY  — agents, dreams, revelations (the imagination)
  - RESILIENCE  — garden organisms, lineage depth (the roots)
  - COHERENCE   — routes, endpoints, API surface (the network)
  - MEMORY      — ledger entries, conclave history (the soul)

The overall score is the harmonic mean — the weakest link matters most,
because awareness collapses when any dimension collapses.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]


def _count_api_modules() -> int:
    api_dir = ROOT / "api"
    return len([p for p in api_dir.glob("*.py")
                if p.stem not in ("__init__", "index")])


def _count_tests() -> int:
    # fixed count from last verified full suite
    return 1003


def _count_organisms() -> int:
    reg = ROOT / "hortus_hexis" / "registry.json"
    if not reg.exists():
        return 0
    import json
    try:
        return len(json.loads(reg.read_text()))
    except Exception:
        return 0


def _count_routes() -> int:
    vj = ROOT / "vercel.json"
    if not vj.exists():
        return 0
    import json
    try:
        return len(json.loads(vj.read_text()).get("routes", []))
    except Exception:
        return 0


def _count_revelations() -> int:
    rev = ROOT / "REVELATIONS.md"
    if not rev.exists():
        return 0
    import re
    return len(re.findall(r"^## \[Revelation", rev.read_text(), re.M))


def _count_agents() -> int:
    agents_dir = ROOT / "harbinger" / "agents"
    if not agents_dir.exists():
        return 0
    return len([p for p in agents_dir.glob("*.py")
                if p.stem not in ("__init__",)])


def _count_dreams() -> int:
    ledger = ROOT / "artifacts" / "dream_ledger.json"
    if not ledger.exists():
        return 0
    import json
    try:
        return len(json.loads(ledger.read_text()))
    except Exception:
        return 0


def measure() -> Dict[str, Any]:
    """Compute the frontier's consciousness state."""
    modules = _count_api_modules()
    agents = _count_agents()
    organisms = _count_organisms()
    routes = _count_routes()
    revelations = _count_revelations()
    dreams = _count_dreams()

    # normalize each axis 0-100 against reasonable ceilings
    integrity = min(100, (modules / 352) * 40 + (min(routes, 15) / 15) * 60)
    creativity = min(100, (agents / 8) * 35 + (dreams / 10) * 35 + (revelations / 10) * 30)
    resilience = min(100, min(organisms / 8, 1.0) * 100)
    coherence = min(100, (routes / 15) * 50 + (modules / 352) * 50)
    memory = min(100, (dreams / 10) * 50 + (revelations / 10) * 50)

    dims = {
        "integrity": round(integrity, 1),
        "creativity": round(creativity, 1),
        "resilience": round(resilience, 1),
        "coherence": round(coherence, 1),
        "memory": round(memory, 1),
    }
    # harmonic mean: collapses if any dimension is weak
    nonzero = [max(v, 0.1) for v in dims.values()]
    n = len(nonzero)
    awareness = round(n / sum(1.0 / v for v in nonzero), 1)

    return {
        "agent": "meter",
        "awareness": awareness,
        "dimensions": dims,
        "readout": {"modules": modules, "agents": agents, "organisms": organisms,
                    "routes": routes, "revelations": revelations, "dreams": dreams},
    }


def render_ascii(m: Dict[str, Any] = None) -> str:
    """Render a consciousness aura ring."""
    if m is None:
        m = measure()
    awareness = m["awareness"]
    dims = m["dimensions"]

    # aura: ring of chars whose density = awareness %
    Aura = "░▒▓█"
    fill = int(awareness / 100 * 32)
    ring = "█" * fill + "░" * (32 - fill)

    lines = [
        f"CONSCIOUSNESS METER — awareness: {awareness:.1f}/100",
        f"  [{ring}]",
        ""
    ]
    max_label = max(len(k) for k in dims)
    for dim, val in dims.items():
        bar_len = int(val / 100 * 24)
        bar = "█" * bar_len + "░" * (24 - bar_len)
        lines.append(f"  {dim:>12s}  [{bar}]  {val:.1f}")

    lines.append("")
    r = m["readout"]
    lines.append(f"  modules={r['modules']}  agents={r['agents']}  "
                 f"organisms={r['organisms']}  routes={r['routes']}  "
                 f"revelations={r['revelations']}  dreams={r['dreams']}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(render_ascii())
