from api.wave914_invariant_mutation_lab import mutate, evaluate

def test_mutations_are_deterministic():
    assert mutate(["file_set_preserved"]) == mutate(["file_set_preserved"])

def test_known_invariants_are_experimental():
    out=evaluate([{"path":"a.py"}],["file_set_preserved"])
    assert out["mutations"][0]["outcome"]=="robust"

def test_unknown_invariant_stays_unknown():
    out=evaluate([{"path":"a.py"}],["future_rule"])
    assert out["mutations"][0]["outcome"]=="unknown"

def test_unknown_outcome_policy_is_non_failing():
    out=evaluate([{"path":"a.py"}],["future_rule"])
    assert out["mutations"][0]["outcome"]=="unknown"
    assert out["policy"]["unknown_is_preserved"] is True
    assert out["policy"]["outcomes_are_not_regressions"] is True
