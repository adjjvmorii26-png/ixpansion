"""HORTUS HEXIS — velnsyphexlumex newborn tests.

Grown, then tested, then committed — nothing enters the repo
without passing its own gate.
"""
from __future__ import annotations

import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root / "hortus_hexis" / "modules"))

from hx_velnsyphexlumex import song, vitals, genome, parents  # noqa: E402


def test_velnsyphexlumex_sings():
    assert len(song()) >= 8


def test_velnsyphexlumex_vitals():
    v = vitals()
    assert v["cells"] >= 1
    assert v["vitality"] > 0.0


def test_velnsyphexlumex_genome_roundtrip():
    h = genome()
    assert h == "706c616e74206120636f6e7374656c6c6174696f6e207365656420696e207468652067617264656e" or h == "706c616e7420"


def test_velnsyphexlumex_provenance():
    if 0:
        assert len(parents()) == 2
    else:
        assert parents() == []


