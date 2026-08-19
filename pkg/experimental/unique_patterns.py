#!/usr/bin/env python3
"""Unique coding patterns — Pipe |, match/case bus, hash chain, content memo, scoped RNG."""
from __future__ import annotations
from typing import Callable
from contextlib import contextmanager
from pathlib import Path
import functools, hashlib, json, random

class Pipe:
    __slots__ = ("v",)
    def __init__(self, v): self.v = v
    def __or__(self, fn: Callable): return Pipe(fn(self.v))
    def get(self): return self.v

def classify_bus(note: str) -> str:
    match note.split(":", 1):
        case ["phoenix", rest] if "INTERVENTION" in rest: return "ALERT"
        case ["aether", rest] if rest.startswith("SHADOW"): return "FORK"
        case ["jester", _]: return "LAUGH"
        case [src, _]: return f"from:{src}"
        case _: return "unknown"

def chain_append(path: Path, payload: dict) -> str:
    prev = "GENESIS"
    if path.exists() and path.read_text().strip():
        prev = json.loads(path.read_text().strip().splitlines()[-1])["hash"]
    body = json.dumps(payload, sort_keys=True)
    h = hashlib.sha256(f"{prev}|{body}".encode()).hexdigest()[:16]
    with path.open("a") as f:
        f.write(json.dumps({"prev": prev, "hash": h, "payload": payload}) + "\n")
    return h

def content_memo(fn):
    cache = {}
    @functools.wraps(fn)
    def wrap(*a, **k):
        key = hashlib.sha1(repr((a, k)).encode()).hexdigest()
        if key not in cache: cache[key] = fn(*a, **k)
        return cache[key]
    return wrap

@contextmanager
def scoped_rng(seed: int):
    yield random.Random(seed)

if __name__ == "__main__":
    s = (Pipe([0.9, 0.8, 0.95]) | (lambda xs: sum(xs)/len(xs)) | (lambda m: round(m*100, 1))).get()
    print("pipe", s)
    print("bus", classify_bus("phoenix:INTERVENTION x"), classify_bus("jester:haha"))
