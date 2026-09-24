from api.wave916_evolution_memory import build, recall

def test_memory_is_deterministic():
    x=[{"id":"m1","content":"preserved","status":"observed","source":"exp-1"}]
    assert build(x)["fingerprint"]==build(x)["fingerprint"]

def test_uncertainty_and_provenance_preserved():
    out=build([{"id":"m1","content":"possible","status":"candidate","source":"exp-1","lineage":["inv-root"]}])
    m=out["memories"][0]
    assert m["status"]=="candidate" and m["source"]=="exp-1"

def test_recall_is_descriptive():
    m={"id":"m1","content":"file set preserved"}
    assert recall(m,"preserved")["match"] is True
