"""Wave 216 — The Organism Bridges: Interstice Bridge.

The Interstice is the organism's bridge cartographer: it scans the
whole repo constellation + every living organ and surfaces latent
kinships that have never been connected. This organ serves those
discoveries inside IXpansion and proposes — for each untouched
bridge — a concrete next action to actually build the connection.

Data is embedded from the generated interstice map (kept in sync
by tools/interstice.py) so the search works anywhere, even serverless.
"""
from __future__ import annotations

from typing import Any, Dict, List

_INTERSTICE_MAP: Dict[str, Any] = {
    "name": "The Interstice",
    "version": "1.0.0",
    "statistics": {
        "repos": 37,
        "organs": 286,
        "untouched_bridges": 75,
        "unique_repos_with_bridges": 28,
    },
    "top_bridges": [
        {"repo": "glitch-cathedral", "organ": "glitch_patterns", "organ_layer": "chaos engineering", "resonance": 0.23},
        {"repo": "quantum-folio", "organ": "quantum_entanglement", "organ_layer": "quantum", "resonance": 0.23},
        {"repo": "nebula-archive", "organ": "memory_palace", "organ_layer": "memory architecture", "resonance": 0.21},
        {"repo": "neuroglyph-forge", "organ": "dream_archaeologist", "organ_layer": "memory archaeology", "resonance": 0.19},
        {"repo": "multiself-engine", "organ": "visual_identity", "organ_layer": "identity", "resonance": 0.18},
        {"repo": "quietus-array", "organ": "silence_composer", "organ_layer": "stillness", "resonance": 0.18},
        {"repo": "quietus-array", "organ": "silence_orchard", "organ_layer": "stillness", "resonance": 0.18},
        {"repo": "neuroglyph-forge", "organ": "nostalgia_engine", "organ_layer": "memory emotion", "resonance": 0.17},
        {"repo": "solid-organism", "organ": "code_organism", "organ_layer": "organism", "resonance": 0.16},
        {"repo": "solid-organism", "organ": "organism_index", "organ_layer": "organism", "resonance": 0.16},
        {"repo": "probability-engine", "organ": "entropy_auction", "organ_layer": "chaos", "resonance": 0.16},
        {"repo": "attention-labyrinth", "organ": "attention_field", "organ_layer": "attention", "resonance": 0.16},
        {"repo": "nexus-observatory", "organ": "observatory_compiler", "organ_layer": "observatory", "resonance": 0.15},
        {"repo": "polychron-atlas", "organ": "temporal_horizon", "organ_layer": "time", "resonance": 0.15},
        {"repo": "chronovore-archive", "organ": "time_capsule", "organ_layer": "time", "resonance": 0.15},
        {"repo": "auric-labyrinth", "organ": "spiral_path_solver", "organ_layer": "sacred", "resonance": 0.14},
        {"repo": "hyperfractal-relay", "organ": "fractal_growth", "organ_layer": "fractal", "resonance": 0.14},
        {"repo": "semiotic-engine", "organ": "metaphor_forge", "organ_layer": "meaning", "resonance": 0.14},
        {"repo": "parallax", "organ": "veil_lifter", "organ_layer": "veil", "resonance": 0.13},
        {"repo": "paraconstruct-engine", "organ": "impossibility_mapper", "organ_layer": "limits", "resonance": 0.13},
    ],
}


def _propose(b: Dict[str, Any]) -> str:
    repo, organ = b["repo"], b["organ"]
    templates = [
        f"Import {organ} as a probe inside {repo} — let it report what it sees.",
        f"Let {organ} emit its state into {repo}'s registry once per cycle.",
        f"Give {repo} a handshake route that calls {organ}'s handler directly.",
        f"Dream a session where {organ} observes {repo}'s evolution and journals it.",
    ]
    idx = (len(repo) + len(organ)) % len(templates)
    return templates[idx]


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "bridge", "status": "resonant", "resonance": 0.83, "wave": 216}


def resonates_with() -> list:
    return ["bridge", "interstice", "untouched", "connection", "cross-project", "latent", "knot"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "map")
    limit = int(payload.get("limit", 10))

    if action == "stats":
        return {"statistics": _INTERSTICE_MAP["statistics"]}

    if action == "propose":
        repo = payload.get("repo")
        organ = payload.get("organ")
        if repo and organ:
            for b in _INTERSTICE_MAP["top_bridges"]:
                if b["repo"] == repo and b["organ"] == organ:
                    return {"bridge": b, "proposal": _propose(b)}
            return {"status": "not_found"}
        out = []
        for b in _INTERSTICE_MAP["top_bridges"][:limit]:
            out.append({"bridge": b, "proposal": _propose(b)})
        return {"proposals": out}

    if action == "by_repo":
        repo = payload.get("repo")
        if not repo:
            return {"status": "error", "error": "repo required"}
        matches = [b for b in _INTERSTICE_MAP["top_bridges"] if b["repo"] == repo]
        return {"repo": repo, "bridges": matches, "count": len(matches)}

    return {
        "map": _INTERSTICE_MAP["top_bridges"][:limit],
        "statistics": _INTERSTICE_MAP["statistics"],
        "note": "These are untouched bridges — latent kinships awaiting their first connection.",
    }
