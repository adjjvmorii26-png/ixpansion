from api.wave918_memory_query import query

def test_query_is_deterministic_and_union_based():
    index={"tokens":{"alpha":["m2","m1"],"beta":["m3","m1"]}}
    out=query(index,"Beta alpha")
    assert out["tokens"]==["alpha","beta"]
    assert out["memory_ids"]==["m1","m2","m3"]

def test_missing_tokens_are_explicit():
    out=query({"tokens":{"alpha":["m1"]}},"alpha missing")
    assert out["memory_ids"]==["m1"]
    assert out["missing_tokens"]==["missing"]

def test_empty_query_is_safe():
    out=query({"tokens":{"alpha":["m1"]}},"")
    assert out["memory_ids"]==[]
    assert out["match_count"]==0
