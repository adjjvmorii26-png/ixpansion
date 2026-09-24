from api.wave908_topology_integrity import build, handler


def test_clean_topology():
    out = build([
        {"record_digest": "a"},
        {"record_digest": "b", "parent": "a"},
    ])
    assert out["anomaly_count"] == 0
    assert out["orphan_parents"] == []


def test_self_cycle():
    out = build([{"record_digest": "a", "parent": "a"}])
    assert out["self_cycles"] == ["a"]
    assert out["cycles"] == [["a"]]


def test_long_cycle_is_explicit():
    out = build([
        {"record_digest": "a", "parent": "c"},
        {"record_digest": "b", "parent": "a"},
        {"record_digest": "c", "parent": "b"},
    ])
    assert out["cycles"] == [["a", "c", "b"]]


def test_orphan_and_duplicate_are_preserved():
    out = build([
        {"record_digest": "x", "parent": "missing"},
        {"record_digest": "x", "parent": "missing"},
    ])
    assert out["duplicate_ids"] == ["x"]
    assert out["orphan_parents"] == ["missing"]


def test_fingerprint_is_replayable():
    records = [{"record_digest": "a", "parent": "a"}]
    assert build(records)["integrity_fingerprint"] == build(records)["integrity_fingerprint"]


def test_status():
    assert handler()["wave"] == 908
