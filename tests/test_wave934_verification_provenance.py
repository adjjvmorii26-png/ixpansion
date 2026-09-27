from api.wave934_verification_provenance import provenance

def test_provenance_reports_present_fields():
    out = provenance({
        "wave": 933,
        "finding": "fingerprints_match",
        "expected_present": True,
        "provided_present": True,
        "match": True,
        "interpretation": "descriptive_verification_explanation_only",
    })
    assert out["source_wave"] == 933
    assert out["source_field_count"] == 6
    assert out["source_fields_missing"] == []

def test_provenance_reports_missing_fields():
    out = provenance({"wave": 933, "finding": "fingerprints_differ"})
    assert out["source_fields_present"] == ["wave", "finding"]
    assert out["source_fields_missing"] == [
        "expected_present",
        "provided_present",
        "match",
        "interpretation",
    ]
    assert out["interpretation"] == "descriptive_provenance_only"

def test_provenance_does_not_make_truth_claims():
    out = provenance({"wave": 933})
    assert "correct" not in out
    assert "truth" not in out
