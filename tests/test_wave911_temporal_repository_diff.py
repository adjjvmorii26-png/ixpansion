from api.wave911_temporal_repository_diff import build

def test_classifies_added_removed_modified():
    out=build([{"path":"a.py","size":1},{"path":"b.py","size":2}],[{"path":"b.py","size":3},{"path":"c.py","size":4}])
    assert out["summary"]=={"added":1,"removed":1,"modified":1}
    assert {x["kind"] for x in out["changes"]}=={"added","removed","modified"}

def test_normalized_fields_preserve_size_and_category():
    out=build([{"path":"a.py","size":1,"category":"source"}],[{"path":"a.py","size":42,"category":"generated"}])
    modified=out["changes"][0]
    assert modified["before"]=={"path":"a.py","size":1,"category":"source"}
    assert modified["after"]=={"path":"a.py","size":42,"category":"generated"}
    assert modified["status"]=="changed"

def test_replayable():
    x=[{"path":"a.py","size":1}]
    assert build(x,x)["fingerprint"]==build(x,x)["fingerprint"]

def test_change_not_regression_policy():
    assert build([], [{"path":"a.py"}])["policy"]["change_is_not_regression"]

def test_changes_are_canonically_ordered_by_path_then_kind():
    before=[{"path":"b.py","size":1},{"path":"a.py","size":1}]
    after=[{"path":"b.py","size":2},{"path":"c.py","size":1}]
    out=build(before,after)
    assert [(x["path"],x["kind"]) for x in out["changes"]]==[("a.py","removed"),("b.py","modified"),("c.py","added")]


def test_semantic_behavior_policy_is_non_inferential():
    out=build([], [{"path":"a.py"}])
    assert out["policy"]["semantic_behavior_not_inferred"] is True
    assert out["policy"]["classification_is_descriptive"] is True


def test_handler_defaults_to_status():
    from api.wave911_temporal_repository_diff import handler
    assert handler()=={"wave":911,"name":"temporal_repository_diff","status":"experimental"}
