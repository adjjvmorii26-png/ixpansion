from api.wave907_branch_atlas import build, handler


def test_depth_and_paths_are_deterministic():
    records = [
        {"record_digest": "root"},
        {"record_digest": "b", "parent": "root"},
        {"record_digest": "c", "parent": "root"},
        {"record_digest": "d", "parent": "b"},
    ]
    out = build(records)
    assert out == build(list(reversed(records)))
    assert out["depth"]["d"] == 2
    assert out["terminal_paths"][0]["path"] == ["root", "b", "d"]


def test_branch_point_is_structural_only():
    out = build([
        {"record_digest": "a"},
        {"record_digest": "b", "parent": "a"},
        {"record_digest": "c", "parent": "a"},
    ])
    assert out["branch_points"] == [{"node": "a", "children": 2, "children_ids": ["b", "c"]}]


def test_orphan_is_preserved():
    out = build([{"record_digest": "b", "parent": "missing"}])
    assert out["orphan_parents"] == ["missing"]


def test_status():
    assert handler()["wave"] == 907
