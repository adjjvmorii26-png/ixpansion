from api.wave933_verification_explainability import explain

def test_matching_verification_is_explained():
    out = explain({
        "match": True,
        "expected_fingerprint": "abc",
        "provided_fingerprint": "abc",
    })
    assert out["finding"] == "fingerprints_match"
    assert out["match"] is True
    assert out["expected_present"] is True
    assert out["provided_present"] is True

def test_difference_is_explained_without_judgment():
    out = explain({
        "match": False,
        "expected_fingerprint": "abc",
        "provided_fingerprint": "xyz",
    })
    assert out["finding"] == "fingerprints_differ"
    assert out["match"] is False
    assert "correct" not in out
    assert "truth" not in out

def test_missing_values_remain_descriptive():
    out = explain({"match": False})
    assert out["expected_present"] is False
    assert out["provided_present"] is False
    assert out["interpretation"] == "descriptive_verification_explanation_only"
