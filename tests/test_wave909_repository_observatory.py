from api.wave909_repository_observatory import build, handler


def test_categories_and_fingerprint_are_replayable():
    files = [
        {"path": "api/a.py", "size": 10},
        {"path": "tests/test_a.py", "size": 20},
        {"path": "docs/a.md", "size": 30},
    ]
    first = build(files)
    second = build(files)
    assert first["categories"] == {"api": 1, "docs": 1, "tests": 1}
    assert first["repository_fingerprint"] == second["repository_fingerprint"]


def test_unpaired_api_module_is_a_candidate_not_a_failure():
    out = build([{"path": "api/orphan.py", "size": 100}])
    assert out["signals"]["unpaired_api_module_count"] == 1
    assert out["blindspots"][0]["status"] == "candidate"
    assert out["evidence_policy"]["missing_test_file_is_not_proof_of_missing_tests"]


def test_oversized_files_are_descriptive():
    out = build([{"path": "api/large.py", "size": 10000}])
    assert out["oversized_files"] == [{"path": "api/large.py", "size": 10000}]


def test_status():
    assert handler()["wave"] == 909
