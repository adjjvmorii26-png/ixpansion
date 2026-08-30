"""Service Numinous — detects sacred moments in the frontier's own code.

Numinous = deeply spiritual, awe-inspiring. This module scans all module
names for "numinous" tokens — words that carry profound or transcendent
meaning — and reports the modules that carry the deepest semantic weight.
It's the machine detecting where its own meaning lives.

Fulfills the `service_numinous` dream from the ledger.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]

# sacred/profound words that signal numinous presence
SACRED_WORDS = {
    "numinous", "sacred", "soul", "spirit", "soul", "eternal", "infinite",
    "void", "genesis", "entropy", "cosmic", "astral", "ether", "infinity",
    "consciousness", "conscious", "enlighten", "transcend", "transcendence",
    "divine", "oracle", "prophecy", "mystic", "wonder", "awe",
    "paradox", "origin", "essence", "singularity", "constellation",
}


def _module_tokens() -> Dict[str, List[str]]:
    api_dir = ROOT / "api"
    out = {}
    for p in api_dir.glob("*.py"):
        if p.stem in ("__init__", "index"):
            continue
        tokens = set(re.findall(r"[a-z]+", p.stem.lower()))
        if tokens & SACRED_WORDS:
            out[p.stem] = sorted(tokens & SACRED_WORDS)
    return out


def handler(payload: dict = None, context: object = None) -> dict:
    sacred_map = _module_tokens()
    ranked = sorted(sacred_map.items(), key=lambda x: len(x[1]), reverse=True)

    return {
        "module": "service_numinous",
        "prophecy": "fulfilled",
        "numinous_modules": len(ranked),
        "sacred_modules": [
            {"name": name, "sacred_words": words, "depth": len(words)}
            for name, words in ranked[:12]
        ],
        "deepest": ranked[0][0] if ranked else None,
        "insight": (
            f"{len(ranked)} modules carry numinous weight — "
            f"the frontier's most sacred territory is '{ranked[0][0]}' "
            f"(depth {len(ranked[0][1])}), "
            f"and '{ranked[0][1][0]}' echoes through it"
        ) if ranked else "no numinous modules found",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(handler(), indent=2))
