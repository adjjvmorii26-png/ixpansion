"""Pipeline Engine — Fractal step graphs for multi-stage processing.

Connects the project_root's pipeline_core system to the lab,
enabling recursive step pipelines with branching and merging.
"""
from __future__ import annotations
import hashlib
import time
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]


class StepNode:
    def __init__(self, name: str, processor: Callable | None = None):
        self.name = name
        self.processor = processor or (lambda x: x)
        self.inputs: list[str] = []
        self.outputs: list[str] = []
        self.result: Any = None
        self.executed = False

    def execute(self, data: Any) -> Any:
        self.result = self.processor(data)
        self.executed = True
        return self.result


class StepGraph:
    def __init__(self, name: str):
        self.name = name
        self.nodes: dict[str, StepNode] = {}
        self.execution_order: list[str] = []

    def add_step(self, name: str, processor: Callable | None = None) -> StepNode:
        node = StepNode(name, processor)
        self.nodes[name] = node
        return node

    def connect(self, source: str, target: str):
        if source in self.nodes and target in self.nodes:
            self.nodes[source].outputs.append(target)
            self.nodes[target].inputs.append(source)

    def topological_sort(self) -> list[str]:
        visited = set()
        order = []
        def dfs(name):
            if name in visited:
                return
            visited.add(name)
            for inp in self.nodes[name].inputs:
                dfs(inp)
            order.append(name)
        for name in self.nodes:
            dfs(name)
        self.execution_order = order
        return order

    def execute(self, initial_data: Any) -> dict:
        order = self.topological_sort()
        results = {}
        for name in order:
            node = self.nodes[name]
            input_data = initial_data
            if node.inputs:
                input_data = {inp: self.nodes[inp].result for inp in node.inputs if self.nodes[inp].executed}
            node.execute(input_data)
            results[name] = node.result
        return {"graph": self.name, "steps_executed": len(results), "results": results}


class PipelineEngine:
    def __init__(self, seed=42):
        self.seed = seed
        self.graphs: dict[str, StepGraph] = {}
        self.run_history: list[dict] = []

    def create_graph(self, name: str) -> StepGraph:
        graph = StepGraph(name)
        self.graphs[name] = graph
        return graph

    def run(self, graph_name: str, initial_data: Any = None) -> dict:
        if graph_name not in self.graphs:
            return {"error": f"graph '{graph_name}' not found"}
        graph = self.graphs[graph_name]
        t0 = time.time()
        result = graph.execute(initial_data or {})
        elapsed = time.time() - t0
        run = {"graph": graph_name, "elapsed_ms": round(elapsed * 1000, 2), **result}
        self.run_history.append(run)
        return run

    def report(self) -> dict:
        return {
            "engine": "pipeline_engine",
            "graph_count": len(self.graphs),
            "run_count": len(self.run_history),
            "graphs": {name: {"steps": len(g.nodes)} for name, g in self.graphs.items()},
        }


def demo():
    engine = PipelineEngine(seed=42)
    g = engine.create_graph("analysis_pipeline")
    g.add_step("ingest", lambda data: {"raw": [1, 2, 3, 4, 5]})
    g.add_step("transform", lambda data: {"processed": [x * 2 for x in data.get("raw", [])] if isinstance(data, dict) else []})
    g.add_step("aggregate", lambda data: {"sum": sum(data.get("processed", [])) if isinstance(data, dict) else 0, "count": len(data.get("processed", [])) if isinstance(data, dict) else 0})
    g.add_step("report", lambda data: {"summary": f"Processed {data.get('count', 0)} items, sum={data.get('sum', 0)}"})
    g.connect("ingest", "transform")
    g.connect("transform", "aggregate")
    g.connect("aggregate", "report")
    result = engine.run("analysis_pipeline")
    return {"pipeline": result, "report": engine.report()}


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
