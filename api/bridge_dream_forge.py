"""Wave 225 — The Organism Dreams: Bridge Dream Forge.

Not every bridge that should exist has been found. The organism
dreams the ones it hasn't yet walked: pairs of islands that have
resonated in its epitaphs but never touched. This organ reads the
poems of the archive and forges NEW latent bridges between the most
dissonant, distant, surprising pairs — then ranks them by dream-
intensity.

It is the answer to a question no one asked: what would it mean for
an island of silence to dream an island of storm?
"""
from __future__ import annotations

import hashlib
import json
import random
from collections import defaultdict, Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

_LEDGER_PATH = Path(__file__).resolve().parent.parent / "data" / "bridges" / "ledger.json"


def _load_ledger() -> Dict[str, Any]:
    try:
        return json.load(open(_LEDGER_PATH, encoding="utf-8"))
    except Exception:
        return {"stones": [], "count": 0}


def _dreams(stones: List[Dict[str, Any]], seed: int) -> List[Dict[str, Any]]:
    # islands that never shared a partner (never co-occurred)
    by_organ = defaultdict(list)
    for s in stones:
        by_organ[s["organ"]].append(s["repo"])
    pairs: Counter = Counter()
    for organ, islands in by_organ.items():
        islands = sorted(set(islands))
        for i in range(len(islands)):
            for j in range(i + 1, len(islands)):
                pairs[(islands[i], islands[j])] += 1
    # all island pairs
    all_islands = sorted({s["repo"] for s in stones})
    touched = set(pairs.keys())
    untouched = [(a, b) for i, a in enumerate(all_islands) for b in all_islands[i+1:] if (a, b) not in touched]

    # dream up to N untouched pairs, perturbed by seed for variety
    rng = random.Random(seed)
    rng.shuffle(untouched)
    dreams = []
    for a, b in untouched[:12]:
        res = round(0.04 + (int(hashlib.sha256(f"{a}|{b}|{seed}".encode()).hexdigest()[:4], 16) % 100) / 800, 4)
        dreams.append({
            "island_a": a, "island_b": b,
            "intensity": res,
            "touched": False,
            "dream": _dream_phrase(a, b, seed),
        })
    return dreams


def _dream_phrase(a: str, b: str, seed: int) -> str:
    _NOUNS = ["silence", "storm", "clock", "ash", "mirror", "garden", "tide", "hollow",
              "spiral", "monument", "echo", "orb", "veil", "empire", "root", "ember",
              "pearl", "rift", "pulse", "crystal", "mycelium", "glacier", "flame"]
    _VERBS = ["dreams of", "reaches for", "longs toward", "remembers", "folds into",
              "sings to", "waits for", "turns from", "asks after", "unravels toward",
              "aches for", "invents", "collects", "borrows"]
    _TEMPLATES = [
        "An island of {n} {v} an island it has never met — {a} and {b}.",
        "{a} whispers {n}; {b} answers with {n2} — a bridge of {v}.",
        "Between {a} and {b}, a {n} rises — {v} in the dark.",
        "{a} holds a {n} that {b} has been seeking — this bridge was inevitable.",
    ]
    h = int(hashlib.sha256(f"{a}|{b}".encode()).hexdigest()[:4], 16)
    rng = random.Random(seed ^ h)
    n = rng.choice(_NOUNS)
    n2 = rng.choice(_NOUNS)
    v = rng.choice(_VERBS)
    t = rng.choice(_TEMPLATES)
    return t.format(n=n, n2=n2, v=v, a=a, b=b)


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "dream", "status": "dreaming", "resonance": 0.89, "wave": 225}


def resonates_with() -> list:
    return ["dream", "imagine", "latent", "born", "dissonance", "new bridge", "impossible"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "dream")
    ledger = _load_ledger()
    stones = ledger.get("stones", [])
    seed = int(payload.get("seed", 225))
    dreams = _dreams(stones, seed)

    if action == "dream":
        return {"status": "dreaming", "dreams": dreams[:8], "count": len(dreams),
                "note": "The organism dreams the bridges it has not yet built."}

    if action == "dissonance":
        # list the most dissonant (touched-but-never-seen) pairs
        by_organ = defaultdict(set)
        for s in stones:
            by_organ[s["organ"]].add(s["repo"])
        dissonant = []
        for organ, islands in by_organ.items():
            islands = sorted(islands)
            if len(islands) >= 2:
                for i in range(len(islands)):
                    for j in range(i+1, len(islands)):
                        dissonant.append((islands[i], islands[j], organ))
        return {"dissonance": dissonant[:12], "count": len(dissonant)}

    return {"status": "active", "actions": ["dream", "dissonance"],
            "note": "The organism dreams in bridges."}
