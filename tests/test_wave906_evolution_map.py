from api.wave906_evolution_map import build, handler

def test_replayable_and_sorted():
    r=[{"record_digest":"b","parent":"a"},{"record_digest":"a"}]
    assert build(r)==build(r)
    assert build(r)["roots"]==["a"]

def test_divergence():
    out=build([{"record_digest":"a"},{"record_digest":"b","parent":"a"},{"record_digest":"c","parent":"a"}])
    assert out["divergence"]==[{"node":"a","children":2}]

def test_orphan_parent():
    out=build([{"record_digest":"b","parent":"missing"}])
    assert out["orphan_parents"]==["missing"]

def test_status():
    assert handler()["wave"]==906
