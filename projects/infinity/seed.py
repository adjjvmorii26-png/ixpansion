#!/usr/bin/env python3
"""Infinity seed — mutates its own next question from body state."""
import hashlib, json, time
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ixpansion/organism-console"))
try:
    from engine import load, ensure_scores
except Exception:
    load = None

QUESTIONS = [
    "if the bus forgot one note which would matter",
    "what if score were a direction not a height",
    "which organ should dream next",
    "can two stewards share one fingerprint",
    "what does synchronicity refuse to measure",
    "where does phoenix rest when nothing falls",
    "what lattice-wire cannot carry",
    "tea in the capsule: ritual or bug",
]

def main():
    score, n_agents = 99.0, 47
    if load:
        try:
            st = ensure_scores(load())
            score = float(st.get("body_score") or score)
            n_agents = len(st.get("agents") or [])
        except Exception:
            pass
    h = hashlib.sha256(f"{score}{n_agents}{time.time()//60}".encode()).hexdigest()
    q = QUESTIONS[int(h[:8], 16) % len(QUESTIONS)]
    log = Path(__file__).resolve().parent / "path.jsonl"
    rec = {"ts": time.time(), "q": q, "score": score, "fp": h[:12]}
    with log.open("a") as f:
        f.write(json.dumps(rec) + "\n")
    print(f"path · {q}")
    print(f"seed · {h[:12]} score={score}")

if __name__ == "__main__":
    main()
