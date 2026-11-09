"""Property-based adversarial tests for cross-system contract validators.

These tests import the production-facing validators from the contract modules;
they do not maintain shadow implementations that can drift away from them.
"""
from hypothesis import given, settings, strategies as st

from tests.contracts.test_conductor_handoff import validate_handoff
from tests.contracts.test_gitlab_guard import validate_pipeline
from tests.contracts.test_vercel_gate import validate_vercel_manifest


HEX_SHA = st.text(alphabet="0123456789abcdef", min_size=40, max_size=40)
PROJECT_IDS = st.text(min_size=1, max_size=80).filter(lambda value: bool(value.strip()))
ENVIRONMENTS = st.sampled_from(["preview", "production"])


@settings(max_examples=150, deadline=None)
@given(
    project_id=st.one_of(st.none(), st.text(max_size=80), PROJECT_IDS),
    commit_sha=st.one_of(st.text(max_size=80), HEX_SHA),
    environment=st.one_of(st.text(max_size=20), ENVIRONMENTS),
)
def test_vercel_manifest_never_raises_and_accepts_valid_generated_manifests(
    project_id, commit_sha, environment
):
    manifest = {
        "project_id": project_id,
        "commit_sha": commit_sha,
        "environment": environment,
    }
    result = validate_vercel_manifest(manifest)
    assert isinstance(result, bool)

    if (
        isinstance(project_id, str)
        and bool(project_id)
        and isinstance(commit_sha, str)
        and len(commit_sha) == 40
        and all(char in "0123456789abcdefABCDEF" for char in commit_sha)
        and environment in {"preview", "production"}
    ):
        assert result is True


@settings(max_examples=150, deadline=None)
@given(
    pipeline=st.dictionaries(
        keys=st.text(min_size=1, max_size=30),
        values=st.one_of(
            st.none(),
            st.booleans(),
            st.integers(),
            st.text(max_size=80),
            st.lists(st.one_of(st.text(max_size=40), st.integers()), max_size=5),
            st.dictionaries(
                keys=st.sampled_from(["stage", "script", "dependencies"]),
                values=st.one_of(
                    st.text(max_size=40),
                    st.lists(st.text(max_size=40), max_size=5),
                    st.integers(),
                    st.none(),
                ),
                max_size=3,
            ),
        ),
        max_size=8,
    )
)
def test_gitlab_pipeline_arbitrary_topologies_never_raise(pipeline):
    result = validate_pipeline(pipeline)
    assert isinstance(result, bool)


@settings(max_examples=150, deadline=None)
@given(
    step_id=st.one_of(st.none(), st.text(max_size=80)),
    status=st.sampled_from(["partial", "complete", "failed", "unknown"]),
    compensation_ref=st.one_of(st.none(), st.text(max_size=80)),
    atomicity_claimed=st.booleans(),
)
def test_conductor_handoff_partial_state_never_overclaims_atomicity(
    step_id, status, compensation_ref, atomicity_claimed
):
    handoff = {
        "step_id": step_id,
        "status": status,
        "compensation_ref": compensation_ref,
        "atomicity_claimed": atomicity_claimed,
    }
    result = validate_handoff(handoff)
    assert isinstance(result, bool)

    if status == "partial" and atomicity_claimed is True:
        assert result is False
    if status == "partial" and not compensation_ref:
        assert result is False


@settings(max_examples=100, deadline=None)
@given(value=st.one_of(st.none(), st.booleans(), st.integers(), st.text(), st.lists(st.integers())))
def test_all_validators_reject_non_mapping_top_level_inputs(value):
    assert validate_vercel_manifest(value) is False
    assert validate_pipeline(value) is False
    assert validate_handoff(value) is False
