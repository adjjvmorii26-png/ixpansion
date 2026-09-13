#!/usr/bin/env python3
"""Decade Compass — map a question onto 10y need-axes."""
from __future__ import annotations
import json, hashlib, sys
from datetime import datetime, timezone
AXES = ("contract_stability", "intentional_oblivion", "proof_density", "dual_sovereignty", "atlas_interface", "agent_lifecycle", "compute_humility", "fail_closed_bridges")
def score(question: str) -> dict:
    h = hashlib.sha256((question or "need").encode()).digest()
    weights = {AXES[i]: round(h[i] / 255.0, 3) for i in range(len(AXES))}
    top = sorted(weights, key=weights.get, reverse=True)[:3]
    frames = [{"t": "0.0s", "role": "hook", "text": "DECADE COMPASS", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": " · ".join(top[:2]), "style": "magenta"}, {"t": "5.0s", "role": "live", "text": top[2], "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · expand meaning, compress map", "style": "dim"}]
    return {"ok": True, "project": "decade_compass", "weights": weights, "priority": top, "frames": frames, "audio": None, "doctrine": "expand the meaning surface, compress the map", "ts": datetime.now(timezone.utc).isoformat()}
def main():
    print(json.dumps(score(" ".join(sys.argv[1:]) or "what does IXPANSION need in ten years"), indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
