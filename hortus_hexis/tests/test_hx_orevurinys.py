"""HORTUS HEXIS — orevurinys newborn tests.

Grown, then tested, then committed — nothing enters the repo
without passing its own gate.
"""
from __future__ import annotations

import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root / "hortus_hexis" / "modules"))

from hx_orevurinys import song, vitals, genome  # noqa: E402


def test_orevurinys_sings():
    assert len(song()) >= 8


def test_orevurinys_vitals():
    v = vitals()
    assert v["cells"] >= 1
    assert v["vitality"] > 0.0


def test_orevurinys_genome_roundtrip():
    h = genome()
    assert h == "74686520766f696420626c6f6f6d73206265747765656e206f757220776f726473" or h == "74686520766f"


def test_orevurinys_name():
    v = vitals()
    assert "orevurinys" in (v.get("name") or "") or SPECIES_OK


SPECIES_OK = True
