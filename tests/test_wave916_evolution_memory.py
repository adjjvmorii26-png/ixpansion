import pytest
from api.wave916_evolution_memory import build, recall

def test_memory_is_deterministic():
    x=[{"id":"m1","content":"preserved","status":"observed","source":"exp-1"}]
    assert build(x)["fingerprint"]==build(x)["fingerprint"]

def test_uncertainty_and_provenance_preserved():
    out=build([{"id":"m1","content":"possible","status":"candidate","source":"exp-1","lineage":["inv-root"]}])
    m=out["memories"][0]
    assert m["status"]=="candidate" and m["source"]=="exp-1"

def test_missing_provenance_is_rejected():
    with pytest.raises(ValueError, match="source is required"):
        build([{"id":"m1","content":"untraceable"}])

def test_recall_preserves_context():
    m={"id":"m1","content":"file set preserved","status":"candidate","source":"exp-1","lineage":["root"]}
    out=recall(m,"preserved")
    assert out["match"] is True
    assert out["status"]=="candidate" and out["source"]=="exp-1" and out["lineage"]==["root"]
