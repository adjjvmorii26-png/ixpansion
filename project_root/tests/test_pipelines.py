import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from nucleus.pipeline_core.pipeline_engine import PipelineEngine
from nucleus.pipeline_core.fractal_steps.step_node import StepNode


class TestStepNode:
    def test_simple_step(self):
        node = StepNode("step1", handler=lambda ctx: ctx.get("input", 0) + 1)
        result = node.execute({"input": 5})
        assert result.success
        assert result.output == 6

    def test_failing_step(self):
        def bad_handler(ctx):
            raise ValueError("boom")
        node = StepNode("bad", handler=bad_handler)
        result = node.execute({})
        assert not result.success
        assert "boom" in result.error


class TestFractalNesting:
    def test_nested_steps(self):
        root = StepNode("root", handler=lambda c: "root_done")
        child1 = StepNode("child1", handler=lambda c: "child1_done")
        child2 = StepNode("child2", handler=lambda c: "child2_done")
        root.add_child(child1)
        child1.add_child(child2)

        result = root.execute({})
        assert result.total_steps == 3
        assert result.success

    def test_max_depth_enforced(self):
        root = StepNode("root", max_depth=2)
        c1 = StepNode("c1")
        c2 = StepNode("c2")
        c3 = StepNode("c3")
        root.add_child(c1)
        c1.add_child(c2)
        with pytest.raises(RecursionError):
            c2.add_child(c3)


class TestPipelineEngine:
    def test_add_and_execute(self):
        engine = PipelineEngine()
        engine.add_step("step_a", handler=lambda c: c.get("x", 0))
        engine.add_step("step_b", handler=lambda c: c.get("x", 0) + 100)
        result = engine.execute({"x": 42})
        assert result["all_success"] is True
        assert result["steps_executed"] == 2

    def test_run_count(self):
        engine = PipelineEngine()
        engine.add_step("s", handler=lambda c: None)
        engine.execute({})
        engine.execute({})
        assert engine.run_count == 2
