#!/usr/bin/env python3
"""Forge Mind — deterministic symbolic triage for ritual phrases."""
from __future__ import annotations

import argparse
import hashlib
import json
from typing import Any


RITUALS = {
    "error": ("repair", "fracture detected; bind a reversible seam"),
    "status": ("observe", "collapse the signal into an inspectable ledger"),
    "design": ("shape", "draft a bounded prototype before expansion"),
    "expand": ("branch", "grow only through an isolated shadow lane"),
}


def respond(phrase: str) -> dict[str, Any]:
    normalized = " ".join(phrase.lower().split())
    ritual, response = next(
        ((ritual, response) for token, (ritual, response) in RITUALS.items() if token in normalized),
        ("witness", "preserve the phrase as an unresolved anomaly"),
    )
    fingerprint = hashlib.sha256([normalized, ritual, response].__str__().encode()).hexdigest()[:16]
    return {
        "agent": "forge_mind",
        "input": phrase,
        "normalized": normalized,
        "ritual": ritual,
        "response": response,
        "fingerprint": fingerprint,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Ask Forge Mind for deterministic symbolic triage")
    parser.add_argument("phrase", nargs="+")
    args = parser.parse_args()
    print(json.dumps(respond(" ".join(args.phrase)), sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
