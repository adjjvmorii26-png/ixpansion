import pytest
from omega_prime.protocols.hex.encoder import frame
from omega_prime.protocols.hex.decoder import unframe
from omega_prime.nucleus.utilities.exception_map import HexDecodeError, HexEncodeError


class TestHexRoundTrip:
    @pytest.mark.parametrize("dialect", [1, 2])
    def test_round_trip(self, dialect):
        payload = {"agent": "scout-01", "action": "move", "target": [3, 7]}
        raw = frame(payload, dialect=dialect)
        decoded = unframe(raw)
        if dialect == 1:
            # Alpha strips nested lists
            assert decoded["agent"] == "scout-01"
            assert decoded["action"] == "move"
        elif dialect == 2:
            assert decoded["body"]["agent"] == "scout-01"

    def test_invalid_dialect_raises(self):
        with pytest.raises(HexEncodeError):
            frame({"x": 1}, dialect=99)

    def test_short_frame_raises(self):
        with pytest.raises(HexDecodeError):
            unframe(b"\x00\x00")

    def test_bad_magic_raises(self):
        raw = frame({"ok": True}, dialect=1)
        corrupted = b"\xff\xff" + raw[2:]
        with pytest.raises(HexDecodeError):
            unframe(corrupted)
