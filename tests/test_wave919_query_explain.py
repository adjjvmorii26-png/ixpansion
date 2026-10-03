from api.wave919_query_explain import explain

def test_explanation_is_deterministic():
    r={"query":"beta alpha","tokens":["alpha","beta"],"memory_ids":["m2","m1"],"missing_tokens":["gamma"],"match_count":2}
    assert explain(r)==explain(r)

def test_explanation_has_no_ranking_or_confidence():
    out=explain({"query":"alpha","tokens":["alpha"],"memory_ids":["m1"],"missing_tokens":[],"match_count":1})
    assert out["method"]=="token_union"
    assert out["interpretation"]=="descriptive_retrieval_only"
    assert "rank" not in out and "confidence" not in out


def test_explanation_canonically_orders_ids_and_missing_tokens():
    out=explain({"query":"beta alpha","tokens":["beta","alpha"],"memory_ids":["m2","m1"],"missing_tokens":["zeta","alpha"],"match_count":2})
    assert out["matched_memory_ids"]==["m1","m2"]
    assert out["missing_tokens"]==["alpha","zeta"]
