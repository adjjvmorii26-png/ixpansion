from api.wave914_invariant_mutation_lab import mutate, evaluate

def test_mutations_are_deterministic():
    assert mutate(["file_set_preserved"]) == mutate(["file_set_preserved"])

def test_known_invariants_are_experimental():
    out=evaluate([{"path":"a.py"}],["file_set_preserved"])
    assert out["mutations"][0]["outcome"]=="robust"

def test_unknown_invariant_stays_unknown():
    out=evaluate([{"path":"a.py"}],["future_rule"])
    assert out["mutations"][0]["outcome"]=="unknown"


def test_duplicate_invariants_are_collapsed():
    out=mutate(["file_set_preserved","file_set_preserved","future_rule"])
    assert [item["source"] for item in out]==["file_set_preserved","future_rule"]
