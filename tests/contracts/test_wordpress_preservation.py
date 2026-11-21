"""Preserve custom and unknown WordPress block payloads."""
import json


def round_trip_blocks(blocks):
    return json.loads(json.dumps(blocks, ensure_ascii=False))


def test_block_preservation(wp_payload):
    original = wp_payload["custom_block_tree"]
    restored = round_trip_blocks(original)
    assert restored == original
    assert restored[0]["blockName"] == "ixpansion/telemetry-hud"
    assert restored[0]["attrs"] == {"theme": "dark-hex", "refreshRate": 1000}
    assert restored[0]["innerBlocks"][0]["blockName"] == "core/paragraph"
    # Unknown vendor blocks must survive unchanged, not be silently discarded.
    assert restored[1] == original[1]
