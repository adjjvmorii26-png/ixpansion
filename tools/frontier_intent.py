"""Frontier Intent — what is this codebase actually about?

Reads every module name, reduces it to tokens, and clusters the tokens
into "intents" — the recurring obsessions of the frontier. Reports the
top themes, emerging interests (recent modules' leanings), and the
frontier's current "focus vector" as a compact summary.

    python tools/frontier_intent.py
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "api"

# mapping of intent families; fall back to single-word topics
THEME_FAMILIES = {
    "dream": {"dream", "dreamer", "dreamweaver", "dreamcatcher", "prophecy", "vision", "oracle", "prophe"},
    "economy": {"market", "price", "econom", "commerce", "trade", "billing", "bank", "revenue", "fee", "currency"},
    "cosmos": {"quantum", "star", "constellation", "galaxy", "space", "cosmic", "nebula", "astro", "pulsar", "celestial"},
    "intelligence": {"agent", "intellig", "cogni", "neural", "mind", "conscious", "reason", "logic", "cognition", "learning"},
    "chaos": {"chaos", "entropy", "random", "glitch", "turbulence", "fractal", "paradox", "anomal"},
    "time": {"time", "chrono", "temporal", "timeline", "epoch", "era", "past", "future", "echo", "memory", "chronic"},
    "nature": {"eco", "garden", "flora", "fauna", "mycel", "forest", "bloom", "vine", "organism", "growth", "seed"},
    "system": {"system", "platform", "framework", "core", "kernel", "engine", "runtime", "orchestr", "infrastructure"},
    "society": {"guild", "treaty", "civil", "culture", "social", "federation", "diplomacy", "alliance", "border"},
    "tech": {"api", "server", "web", "http", "cache", "auth", "gateway", "protocol", "queue", "network", "socket"},
    "sensor": {"detect", "observe", "watch", "scan", "monitor", "sensor", "probe", "pulse", "meter", "counter"},
    "weave": {"weav", "loom", "fabric", "braid", "thread", "mesh", "network"},
}


def module_names() -> List[str]:
    if not API_DIR.exists():
        return []
    return sorted(p.stem for p in API_DIR.glob("*.py")
                  if p.stem not in ("__init__", "index"))


def _tokens(name: str) -> List[str]:
    return re.findall(r"[a-z]+", name.lower())


def _family_of(token: str) -> str:
    for family, words in THEME_FAMILIES.items():
        if token in words or any(w in token for w in words if len(w) >= 4):
            return family
    return "other"


def analyze() -> Dict[str, Any]:
    names = module_names()
    family_hits: Counter = Counter()
    family_tokens: Dict[str, Counter] = {}
    for name in names:
        toks = _tokens(name)
        seen_families = set()
        for tok in toks:
            fam = _family_of(tok)
            if fam not in seen_families:
                family_hits[fam] += 1
                seen_families.add(fam)
                family_tokens.setdefault(fam, Counter())[tok] += 1

    total = sum(family_hits.values()) or 1
    themes = [
        {"family": fam, "modules_hit": int(n), "share": round(n / total * 100, 1),
         "top_tokens": [w for w, _ in family_tokens[fam].most_common(3)]}
        for fam, n in family_hits.most_common()
    ]

    # focus vector: top 3 families by share
    focus = [t["family"] for t in themes[:3]]

    # emerging interest: tokens that appear ONLY in the newest files (heuristic:
    # sort by token count to approximate complexity; those with exotic tokens)
    exotic = Counter()
    for name in names:
        toks = _tokens(name)
        if any(_family_of(t) == "other" for t in toks):
            for t in toks:
                if _family_of(t) == "other":
                    exotic[t] += 1
    emerging = [tok for tok, _ in exotic.most_common(5)]

    return {
        "tool": "frontier_intent",
        "modules": len(names),
        "themes": themes,
        "focus_vector": focus,
        "emerging_interests": emerging,
        "total_matches": total,
    }


def render(data: Dict[str, Any] = None) -> str:
    if data is None:
        data = analyze()
    lines = [f"FRONTIER INTENT — {data['modules']} modules",
             f"focus vector: {' → '.join(data['focus_vector'])}",
             ""]
    max_family = max(len(t["family"]) for t in data["themes"]) if data["themes"] else 10
    for t in data["themes"]:
        bar = "█" * int(t["share"] * 2)
        lines.append(f"  {t['family']:>{max_family}} [{bar:<20}] {t['share']:>5.1f}%  ({t['modules_hit']} modules, tokens: {', '.join(t['top_tokens'])})")
    lines.append("")
    lines.append(f"  emerging interests: {', '.join(data['emerging_interests']) or 'none'}")
    return "\n".join(lines)


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Frontier intent analyzer")
    ap.add_argument("--json", action="store_true")
    args, _ = ap.parse_known_args(argv)
    data = analyze()
    print(json.dumps(data, indent=2) if args.json else render(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
