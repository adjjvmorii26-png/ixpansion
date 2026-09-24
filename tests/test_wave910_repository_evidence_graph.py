from api.wave910_repository_evidence_graph import build

def test_graph_is_replayable():
    x=[{"id":"o1","claim":"candidate gap","evidence":[{"id":"e1"}]}]
    a=build(x); b=build(x)
    assert a["fingerprint"]==b["fingerprint"]
    assert a["edge_count"]==1

def test_provenance_and_uncertainty_are_preserved():
    out=build([{"id":"o1","claim":"possible gap","status":"candidate","evidence":["e1"]}])
    assert out["graph"]["nodes"][0]["status"]=="candidate"
    assert out["graph"]["edges"][0]["relation"]=="supported_by"
    assert out["policy"]["claims_are_not_truth"]

def test_empty_graph():
    out=build([])
    assert out["node_count"]==0 and out["edge_count"]==0
