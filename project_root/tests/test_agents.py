import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from nucleus.utils.hex_codec import encode, decode, is_hex
from nucleus.utils.entropy import EntropySource
from nucleus.utils.id_gen import generate_id, short_id


class TestHexCodec:
    def test_roundtrip(self):
        original = "hello world"
        assert decode(encode(original)) == original

    def test_is_hex_valid(self):
        assert is_hex("deadbeef")

    def test_is_hex_invalid(self):
        assert not is_hex("not_hex!")


class TestEntropy:
    def test_seeded_reproducible(self):
        e1 = EntropySource(seed=42)
        e2 = EntropySource(seed=42)
        assert e1.int(0, 1000) == e2.int(0, 1000)

    def test_chaos_inject(self):
        e = EntropySource(seed=42)
        state = {"x": 10.0}
        result = e.chaos_inject(state)
        assert result["x"] != 10.0


class TestIdGen:
    def test_generate_id(self):
        id1 = generate_id("test")
        id2 = generate_id("test")
        assert id1 != id2

    def test_short_id_length(self):
        assert len(short_id(8)) == 8
