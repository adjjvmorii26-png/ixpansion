from api.wave915_invariant_genealogy import build

def test_lineage_is_deterministic():
    x=[{"id":"root","name":"file set"},{"id":"child","parents":["root"]}]
    assert build(x)["fingerprint"]==build(x)["fingerprint"]

def test_derived_from_edge():
    out=build([{"id":"root"},{"id":"child","parents":["root"]}])
    assert out["graph"]["edges"]==[{"from":"root","to":"child","relation":"derived_from"}]

def test_unknown_status_preserved():
    out=build([{"id":"x"}])
    assert out["graph"]["nodes"][0]["status"]=="unknown"


def test_origin_provenance_is_preserved():
    out=build([{"id":"child","origin":"wave914","status":"experimental"}])
    assert out["graph"]["nodes"][0]["origin"]=="wave914"
