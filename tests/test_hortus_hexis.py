"""HORTUS HEXIS — garden engine tests (offline-safe, no network/git)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from hortus_hexis.seed import (  # noqa: E402
    words_to_seed, seed_digest, genome_from_hex, species_from_hex, pseudo_word,
)
from hortus_hexis.growth import Organism, _grow_box  # noqa: E402
from hortus_hexis.voice import poem  # noqa: E402
from hortus_hexis.artifacts import safe_name, transcribe  # noqa: E402


def test_seed_chain():
    seed = words_to_seed("hello garden")
    assert seed and all(c in "0123456789abcdef" for c in seed)
    assert species_from_hex(seed)
    g = genome_from_hex(seed)
    assert set(g) == {"rules", "heat", "lethargy"}
    assert len(g["rules"]) == len(g["heat"]) == len(g["lethargy"])


def test_seed_deterministic():
    a = words_to_seed("same words")
    b = words_to_seed("same words")
    assert a == b
    assert seed_digest(a) == seed_digest(b)
    assert species_from_hex(a) == species_from_hex(b)


def test_organism_grows():
    seed = words_to_seed("the void blooms")
    o = Organism("testspore", seed, "the void blooms")
    assert len(o.cells) >= 1
    assert 0.0 < o.vitality <= 1.0
    art = o.to_art()
    assert len(art) >= 5 and isinstance(art[0], str)


def test_grow_box_structure():
    box = _grow_box("aabbccdd")
    assert "cells" in box and "vitality" in box and "width" in box


def test_voice_from_hex():
    seed = words_to_seed("resonance is a river")
    lines = poem(seed, 6, 2)
    assert len(lines) >= 3
    assert "grown from" in lines[-1]


def test_artifacts_transcribe():
    seed = words_to_seed("a small seed")
    p = transcribe("symphys", seed, "a small seed",
                   {"cells": 4, "vitality": 0.5, "depth": 2})
    import json
    spec = json.loads(Path(p["specimen"]).read_text())
    assert spec["name"] == "symphys"
    assert "seed" in spec and "song" in spec
    for path in p.values():
        assert Path(path).exists()
    # cleanup test-only artifacts
    import shutil
    for path in p.values():
        try: Path(path).unlink()
        except FileNotFoundError: pass


def test_safe_name():
    assert safe_name("Orev-u Rin_Ys!") == "orevurin_ys"
    assert safe_name("123") == "123"


def test_pseudo_word():
    seed = words_to_seed("alpha beta gamma delta")
    w = pseudo_word(seed, 1)
    assert w and w.islower()
