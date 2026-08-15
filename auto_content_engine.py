#!/usr/bin/env python3
"""
Autonomous Content Production Engine
Lattice + RAG + genetic discoveries → demo package for @adjjv.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

OUT = Path("/home/workdir/artifacts/content_output/auto_video")
OUT.mkdir(parents=True, exist_ok=True)


def build_demo_script(
    lattice: Optional[dict] = None,
    research_hits: Optional[list] = None,
    genetic: Optional[dict] = None,
    title: str = "IXPANSION Swarm Live Demo",
) -> dict:
    lattice = lattice or {}
    research_hits = research_hits or []
    genetic = genetic or {}

    voiceover = []
    voiceover.append(f"This is an autonomous demonstration from the IXPANSION swarm.")
    if lattice:
        voiceover.append(
            f"Lattice engine {lattice.get('engine', 'unknown')} "
            f"reached final energy {lattice.get('final_energy', 'n/a')} "
            f"on a {lattice.get('n', '?')} by {lattice.get('n', '?')} grid."
        )
    if genetic.get("best_expr"):
        voiceover.append(
            f"The genetic sandbox evolved kernel expression {genetic.get('best_expr')} "
            f"with fitness {genetic.get('best_fitness')}."
        )
    if research_hits:
        voiceover.append("Related research context includes: " +
                         "; ".join(h.get("text", "")[:80] for h in research_hits[:2]))
    voiceover.append("All nodes are signed, load-balanced, and anomaly-monitored.")
    voiceover.append("Subscribe to adjjv for more autonomous systems builds.")

    storyboard = [
        {"t": "0-3s", "visual": "3D constellation camera orbit", "text": "SWARM LIVE"},
        {"t": "3-12s", "visual": "Lattice energy histogram / grid heatmap", "text": "IXPANSION"},
        {"t": "12-25s", "visual": "Genetic fitness curve", "text": "EVOLVING KERNELS"},
        {"t": "25-40s", "visual": "RAG / VSA recall pulses", "text": "SEMANTIC MEMORY"},
        {"t": "40-55s", "visual": "Panel UI + release manifest", "text": "ONE COMMAND SHIP"},
        {"t": "55-60s", "visual": "Logo + CTA", "text": "@adjjv"},
    ]

    package = {
        "id": datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"),
        "title": title,
        "voiceover_script": " ".join(voiceover),
        "voiceover_lines": voiceover,
        "storyboard": storyboard,
        "assets": {
            "lattice": lattice,
            "genetic": {k: genetic.get(k) for k in ("best_expr", "best_fitness", "history") if k in genetic},
            "research": research_hits[:5],
        },
        "render_hints": {
            "resolution": "1920x1080",
            "fps": 30,
            "format": "mp4",
            "source_panels": ["panel/index_3d.html", "panel/index.html"],
            "note": "Capture WebGL canvas via headless Chromium or OBS; voiceover via TTS",
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return package


def produce_auto_package(title: str = "IXPANSION Swarm Live Demo") -> dict:
    lattice = genetic = None
    research_hits = []
    try:
        from swarm_wasm_lattice import run_wasm_lattice
        lattice = run_wasm_lattice(n=12, steps=15, seed=0.42)
    except Exception as e:
        lattice = {"error": str(e)}
    try:
        from genetic_sandbox import evolve
        genetic = evolve(generations=2, population=4)
    except Exception as e:
        genetic = {"error": str(e)}
    try:
        from rag_swarm import RAGIndex
        idx = RAGIndex()
        if not idx.docs:
            idx.add("IXPANSION lattice simulation gossip CRDT mesh", {"type": "seed"})
        research_hits = idx.search("lattice simulation swarm", top_k=3)
    except Exception:
        pass

    pkg = build_demo_script(lattice, research_hits, genetic, title=title)
    path = OUT / f"{pkg['id']}_auto_demo.json"
    path.write_text(json.dumps(pkg, indent=2, default=str))
    md = OUT / f"{pkg['id']}_auto_demo.md"
    lines = [f"# {pkg['title']}", "", "## Voiceover", ""]
    for line in pkg["voiceover_lines"]:
        lines.append(f"- {line}")
    lines += ["", "## Storyboard", ""]
    for s in pkg["storyboard"]:
        lines.append(f"- {s['t']}: {s['visual']} ({s['text']})")
    md.write_text("\n".join(lines))
    print(f"[AutoContent] {path}")
    return pkg


if __name__ == "__main__":
    p = produce_auto_package()
    print(p["voiceover_script"][:300], "...")
  
