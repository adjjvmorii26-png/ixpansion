import pytest
from omega_prime.protocols.hex.glyph_codec import GlyphCodec


class TestGlyphCodec:
    def test_observe_and_learn(self):
        codec = GlyphCodec()
        payload = {"type": "scan", "target": "sector_7"}
        for _ in range(5):
            codec.observe(payload)
        glyph = codec.learn(payload)
        assert glyph is not None

    def test_no_glyph_below_threshold(self):
        codec = GlyphCodec()
        payload = {"rare": True}
        codec.observe(payload)  # Only 1 use
        assert codec.learn(payload) is None

    def test_stats(self):
        codec = GlyphCodec()
        stats = codec.stats
        assert "entries" in stats and "compression_ratio" in stats

    def test_decode_expands(self):
        codec = GlyphCodec()
        payload = {"msg": "hello_world_pattern"}
        for _ in range(3):
            codec.observe(payload)
        glyph = codec.learn(payload)
        encoded = codec.encode(payload)
        decoded = codec.decode(encoded)
        # Should contain the pattern hash somewhere
        assert len(decoded) >= len(encoded)
