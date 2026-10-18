import importlib
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from api.consciousness_state_machine import ConsciousnessStateMachine
from lab.ops import velocity_burst


@pytest.mark.parametrize(
    ("guard", "expected"),
    [
        ("entropy > 0.2", True),
        ("coherence > 0.75 AND entropy > 0.3", True),
        ("entropy > 0.7 AND coherence < 0.4", False),
        ("NOT (entropy < 0.5)", True),
        ("coherence >= 0.5 AND entropy <= 0.5", False),
    ],
)
def test_guard_interpreter_supports_declared_comparison_language(guard, expected):
    assert ConsciousnessStateMachine._check_guard(
        object.__new__(ConsciousnessStateMachine), guard,
        coherence=0.8, entropy=0.6, resonance=0.2,
    ) is expected


@pytest.mark.parametrize(
    "guard",
    [
        "__import__('os').system('echo unsafe')",
        "coherence.__class__",
        "open('/tmp/should-not-exist', 'w')",
        "coherence in [0.8]",
        "coherence ** 2 > 0.1",
        "",
    ],
)
def test_guard_interpreter_rejects_code_and_unsupported_syntax(guard):
    assert ConsciousnessStateMachine._check_guard(
        object.__new__(ConsciousnessStateMachine), guard,
        coherence=0.8, entropy=0.6, resonance=0.2,
    ) is False


def test_guard_interpreter_rejects_non_numeric_runtime_values():
    assert ConsciousnessStateMachine._check_guard(
        object.__new__(ConsciousnessStateMachine), "coherence > 0.5",
        coherence=True, entropy=0.6, resonance=0.2,
    ) is False


def test_velocity_run_requires_argument_vector():
    with pytest.raises(TypeError):
        velocity_burst._run("git status")


def test_velocity_run_never_enables_shell_interpretation():
    completed = SimpleNamespace(stdout="safe output\n", returncode=0)
    with patch.object(velocity_burst.subprocess, "run", return_value=completed) as run:
        assert velocity_burst._run(["git", "status"]) == "safe output"
    assert run.call_args.args[0] == ["git", "status"]
    assert run.call_args.kwargs["shell"] is False


def test_git_history_command_uses_fixed_argument_vector():
    with patch.object(velocity_burst, "_run", return_value="abcdef123456 2026-10-18 12:00:00 +0000") as run:
        result = velocity_burst._git_commits_since(7)
    assert result == [{"hash": "abcdef12", "date": "2026-10-18"}]
    args = run.call_args.args[0]
    assert isinstance(args, list)
    assert args[:2] == ["git", "log"]
    assert "--format=%H %ai" in args
    assert all(";" not in arg for arg in args)


@pytest.mark.parametrize("days", [-1, 36501, True, 1.5, "7"])
def test_git_history_rejects_invalid_windows(days):
    with pytest.raises(ValueError):
        velocity_burst._git_commits_since(days)


def test_visitor_github_mirror_is_disabled_without_explicit_opt_in(monkeypatch):
    monkeypatch.delenv("IXP_ENABLE_GITHUB_MIRROR", raising=False)
    from api import visitor_log
    module = importlib.reload(visitor_log)
    assert module.GITHUB_MIRROR_ENABLED is False


def test_visitor_github_mirror_requires_explicit_truthy_opt_in(monkeypatch):
    monkeypatch.setenv("IXP_ENABLE_GITHUB_MIRROR", "true")
    from api import visitor_log
    module = importlib.reload(visitor_log)
    assert module.GITHUB_MIRROR_ENABLED is True
    monkeypatch.delenv("IXP_ENABLE_GITHUB_MIRROR", raising=False)
    importlib.reload(module)
