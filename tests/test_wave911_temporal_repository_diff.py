from api.wave911_temporal_repository_diff import build

def test_classifies_added_removed_modified():
    out=build([{"path":"a.py","size":1},{"path":"b.py","size":2}],[{"path":"b.py","size":3},{"path":"c.py","size":4}])
    assert out["summary"]=={"added":1,"removed":1,"modified":1}
    assert {x["kind"] for x in out["changes"]}=={"added","removed","modified"}

def test_normalized_fields_preserve_size_and_category():
    out=build([], [{"path":"a.py","size":42,"category":"source"}])
    assert out["changes"][0]["path"]=="a.py"
    assert out["changes"][0]["status"]=="changed"
    assert out["after_fingerprint"]

def test_replayable():
    x=[{"path":"a.py","size":1}]
    assert build(x,x)["fingerprint"]==build(x,x)["fingerprint"]

def test_change_not_regression_policy():
    assert build([], [{"path":"a.py"}])["policy"]["change_is_not_regression"]
