from api.wave920_memory_replay import replay

def test_replay_is_deterministic():
    e={"query":"beta alpha","tokens":["beta","alpha"],"matched_memory_ids":["m2","m1"],"missing_tokens":["gamma"],"method":"token_union"}
    assert replay(e)==replay(e)

def test_replay_contains_explicit_steps():
    out=replay({"query":"alpha","tokens":["alpha"],"matched_memory_ids":["m1"],"missing_tokens":[],"method":"token_union"})
    assert [x["step"] for x in out["steps"]]==["normalize_tokens","resolve_token_union","record_missing_tokens"]
    assert out["replay_only"] is True

def test_replay_does_not_infer_new_results():
    out=replay({"query":"x","tokens":[],"matched_memory_ids":[],"missing_tokens":["x"]})
    assert out["steps"][1]["memory_ids"]==[]
