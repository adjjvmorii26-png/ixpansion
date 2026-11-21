"""Fail-closed validation for deployment manifests."""
import re


def validate_vercel_manifest(manifest):
    if not isinstance(manifest, dict) or not manifest.get("project_id"):
        return False
    sha = manifest.get("commit_sha", "")
    if not isinstance(sha, str) or re.fullmatch(r"[0-9a-fA-F]{40}", sha) is None:
        return False
    return manifest.get("environment") in {"preview", "production"}


def test_valid_manifest_accepted(vercel_data):
    assert validate_vercel_manifest(vercel_data["valid_manifest"]) is True


def test_invalid_sha_blocked(vercel_data):
    assert validate_vercel_manifest(vercel_data["invalid_sha"]) is False


def test_missing_project_and_invalid_environment_blocked(vercel_data):
    manifest = dict(vercel_data["valid_manifest"], project_id="", environment="staging")
    assert validate_vercel_manifest(manifest) is False
