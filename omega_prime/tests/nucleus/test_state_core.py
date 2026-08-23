import pytest
from omega_prime.nucleus.kernel.state_core import StateCore


class TestStateCore:
    def test_set_and_get(self):
        core = StateCore()
        core.set("a.b.c", 42)
        assert core.get("a.b.c") == 42

    def test_get_missing_returns_default(self):
        core = StateCore()
        assert core.get("x.y", "fallback") == "fallback"

    def test_delete(self):
        core = StateCore()
        core.set("key", "val")
        assert core.delete("key") is True
        assert core.delete("key") is False

    def test_snapshot_changes(self):
        core = StateCore()
        s1 = core.snapshot()
        core.set("k", 1)
        s2 = core.snapshot()
        assert s1 != s2

    def test_deepcopy_isolation(self):
        core = StateCore()
        original = {"nested": {"val": [1]}}
        core.set("data", original)
        original["nested"]["val"].append(2)
        assert core.get("data.nested.val") == [1]
