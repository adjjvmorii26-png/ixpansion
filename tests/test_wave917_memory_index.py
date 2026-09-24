from api.wave917_memory_index import build_index, lookup

def test_index_is_deterministic_and_sorted():
    memories=[{"id":"m2","content":"Beta alpha"},{"id":"m1","content":"alpha gamma"}]
    out=build_index(memories)
    assert list(out["tokens"])==["alpha","beta","gamma"]
    assert out["tokens"]["alpha"]==["m1","m2"]

def test_lookup_is_descriptive():
    index=build_index([{"id":"m1","content":"preserved candidate"}])
    assert lookup(index,"preserved")["memory_ids"]==["m1"]
    assert lookup(index,"missing")["memory_ids"]==[]

def test_policy_does_not_rank_or_infer_truth():
    policy=build_index([{"id":"m1","content":"observed"}])["policy"]
    assert policy["descriptive_only"] is True
    assert policy["no_ranking"] is True
    assert policy["no_truth_inference"] is True
