"""Security defaults for the local HORTUS HEXIS HTTP server."""
from inspect import signature

from hortus_hexis import web


def test_garden_server_binds_to_loopback_by_default():
    assert signature(web.serve).parameters["host"].default == "127.0.0.1"


def test_repository_mutations_are_opt_in():
    assert signature(web._plant).parameters["commit"].default is False
    assert signature(web._cross).parameters["commit"].default is False
    assert web._commit_requested({}) is False
    assert web._commit_requested({"commit": False}) is False
    assert web._commit_requested({"commit": "true"}) is False
    assert web._commit_requested({"commit": 1}) is False
    assert web._commit_requested({"commit": True}) is True


def test_local_garden_does_not_emit_wildcard_cors():
    source = (web.ROOT / "hortus_hexis" / "web.py").read_text(encoding="utf-8")
    assert 'Access-Control-Allow-Origin", "*"' not in source
