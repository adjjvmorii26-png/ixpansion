import pytest
from omega_prime.nucleus.kernel.reactor import Reactor


@pytest.mark.asyncio
class TestReactor:
    async def test_emit_calls_handler(self):
        reactor = Reactor()
        results = []

        async def handler(payload):
            results.append(payload)

        reactor.on("test", handler)
        await reactor.emit("test", {"msg": 1})
        assert results == [{"msg": 1}]

    async def test_priority_ordering(self):
        reactor = Reactor()
        order = []

        async def low(p): order.append("low")
        async def high(p): order.append("high")

        reactor.on("evt", low, priority=0)
        reactor.on("evt", high, priority=10)
        await reactor.emit("evt", {})
        assert order == ["high", "low"]

    async def test_handler_error_collected(self):
        reactor = Reactor()

        async def bad(p): raise ValueError("boom")

        reactor.on("evt", bad)
        errors = await reactor.emit("evt", {})
        assert len(errors) == 1
