#!/usr/bin/env python3
"""Glyph Router — soft agent assignment via HEX-tinged hashes."""
from __future__ import annotations
import hashlib, json, math, re, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[3]
GLY = REPO / "lab" / "MONOLITH_STACK" / "PRIME_CORE" / "PRIME_GLYPHS.hex"
AGENTS = ["guardian", "estimator", "scout", "tuner", "synthesizer", "arbiter", "herald", "auditor"]
def bits(s, n=32):
    h = hashlib.sha256(s.encode()).digest()
    out = []
    for byte in h:
        for i in range(8):
            out.append(1 if (byte >> i) & 1 else -1)
            if len(out) >= n: return out
    return out
def cosine(a, b):
    dot = sum(x*y for x,y in zip(a,b))
    na = math.sqrt(sum(x*x for x in a)) or 1
    nb = math.sqrt(sum(x*x for x in b)) or 1
    return dot/(na*nb)
def load_glyphs():
    if not GLY.exists(): return ["SPECS_OUTLIVE", "ETHICS_BEFORE_ACT"]
    return re.findall(r"^G\d+\s+0x[0-9A-Fa-f]+\s+(\S+)", GLY.read_text(), re.M) or ["SPECS_OUTLIVE"]
def route(task):
    glyphs = load_glyphs()
    tv = bits(task)
    ranked = sorted([{"agent": a, "score": round(cosine(tv, bits(a+"|"+glyphs[i%len(glyphs)])), 4)} for i,a in enumerate(AGENTS)], key=lambda x: -x["score"])
    return {"ok": True, "experiment": "glyph_router", "task": task, "primary": ranked[0], "ranked": ranked[:5]}
if __name__ == "__main__":
    print(json.dumps(route(sys.argv[1] if len(sys.argv)>1 else "ethics_gate anomaly orbital"), indent=2))
