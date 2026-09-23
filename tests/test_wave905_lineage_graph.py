from api.wave905_lineage_graph import build, handler

def test_graph_is_replayable():
    r=[{"record_digest":"a"},{"record_digest":"b","parent":"a"}]
    assert build(r)==build(r)

def test_parent_edge():
    out=build([{"record_digest":"a"},{"record_digest":"b","parent":"a"}])
    assert {"from":"a","to":"b","kind":"derived_from"} in out["edges"]
    assert out["roots"]==["a"]

def test_status():
    assert handler()["wave"]==905
