from api.wave914_invariant_mutation_lab import mutate, evaluate

def test_mutations_are_deterministic():
    assert mutate(["file_set_preserved"]) == mutate(["file_set_preserved"])

def test_known_invariants_are_experimental():
    out=evaluate([{"path":"a.py"}],["file_set_preserved"])
    assert out["mutations"][0]["outcome"]=="robust"

def test_unknown_invariant_stays_unknown():
    out=evaluate([{"path":"a.py"}],["future_rule"])
    assert out["mutations"][0]["outcome"]=="unknown"

def test_fingerprint_has_16_hex_characters():
    out=evaluate([{"path":"a.py"}],["file_set_preserved"])
    assert len(out["fingerprint"])==16

def test_preserved_invariant_mutations_tighten():
    out=mutate(["file_set_preserved"])
    assert out[0]["mutation"]=="file_set_strict"
    assert out[0]["kind"]=="tighten"
