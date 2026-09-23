from api.wave908_temporal_echo import echo_map


def test_repeated_fingerprints_form_echoes():
    out = echo_map([
        {"fingerprint": "a"},
        {"fingerprint": "b"},
        {"fingerprint": "a"},
        {"fingerprint": "a"},
    ])
    assert out["echo_count"] == 1
    assert out["echoes"][0]["positions"] == [0, 2, 3]
    assert out["echoes"][0]["gaps"] == [2, 1]


def test_empty_input_is_replayable():
    assert echo_map([])["echoes"] == []
