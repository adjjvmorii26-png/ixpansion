"""Wave 80 tests — HEX VM, CLI, and experimental modules."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


# ─── HEX VM tests ───

class TestHexVM:
    def test_push_and_emit(self):
        from lab.hex_vm import HexVM
        vm = HexVM()
        vm.load_script("PUSH 42\nEMIT\nHALT")
        result = vm.execute()
        assert result["output"] == [42]
        assert result["halted"] is True

    def test_store_and_load(self):
        from lab.hex_vm import HexVM
        vm = HexVM()
        vm.load_script("PUSH 10\nSTORE x\nPUSH 20\nSTORE y\nLOAD x\nLOAD y\nADD\nEMIT\nHALT")
        result = vm.execute()
        assert result["output"] == [30]

    def test_sub(self):
        from lab.hex_vm import HexVM
        vm = HexVM()
        vm.load_script("PUSH 10\nPUSH 3\nSUB\nEMIT\nHALT")
        result = vm.execute()
        assert result["output"] == [7]

    def test_empty_script(self):
        from lab.hex_vm import HexVM
        vm = HexVM()
        vm.load_script("# just a comment\n\n")
        result = vm.execute()
        assert result["steps"] == 0

    def test_load_real_script(self):
        from lab.hex_vm import HexVM
        vm = HexVM()
        script_path = ROOT / "ixpansion" / "src" / "hex" / "scripts" / "agent_rituals.hex"
        if script_path.exists():
            vm.load_file(script_path)
            result = vm.execute()
            assert result["output"] == [7]  # PUSH 3, PUSH 4, ADD = 7

    def test_max_steps_protection(self):
        from lab.hex_vm import HexVM
        vm = HexVM()
        vm.max_steps = 5
        vm.load_script("PUSH 1\nPUSH 2\nPUSH 3\nPUSH 4\nPUSH 5\nPUSH 6\nPUSH 7")
        result = vm.execute()
        assert result["steps"] <= 5

    def test_demo(self):
        from lab.hex_vm import demo
        result = demo()
        assert result["grammar_count"] >= 0
        assert result["script_count"] >= 0


class TestHexGrammarCompiler:
    def test_compile_grammar(self):
        from lab.hex_vm import HexGrammarCompiler
        compiler = HexGrammarCompiler()
        result = compiler.compile("TOPOLOGY star|ring\nCHANNEL reliable\nANOMALY temporal_loop")
        assert "star" in result["topologies"]
        assert "reliable" in result["channels"]
        assert "temporal_loop" in result["anomalies"]

    def test_compile_all_grammars(self):
        from lab.hex_vm import run_all_grammars
        results = run_all_grammars()
        assert isinstance(results, dict)


# ─── Hex Bytecode Compiler tests ───

class TestHexBytecodeCompiler:
    def test_compile_push(self):
        from lab.experiments.hex_bytecode_compiler import HexBytecodeCompiler
        compiler = HexBytecodeCompiler()
        result = compiler.compile_script("test_push", "PUSH 42\nEMIT\nHALT")
        assert "def test_push_hex():" in result["python_source"]
        assert "_stack.append(42)" in result["python_source"]

    def test_compile_store_load(self):
        from lab.experiments.hex_bytecode_compiler import HexBytecodeCompiler
        compiler = HexBytecodeCompiler()
        result = compiler.compile_script("test_store", "PUSH 10\nSTORE x\nLOAD x\nEMIT\nHALT")
        assert "_mem['x']" in result["python_source"]

    def test_compile_all(self):
        from lab.experiments.hex_bytecode_compiler import HexBytecodeCompiler
        compiler = HexBytecodeCompiler()
        modules = compiler.compile_all()
        assert isinstance(modules, list)


# ─── Mutation Network tests ───

class TestMutationNetwork:
    def test_add_nodes_and_edges(self):
        from lab.experiments.mutation_network import MutationNetwork
        net = MutationNetwork(seed=42)
        net.add_node("a", "lab", 300)
        net.add_node("b", "lab", 400)
        edge = net.add_edge("a", "b", "refactor")
        assert edge is not None
        assert edge.cost > 0

    def test_bfs_reachable(self):
        from lab.experiments.mutation_network import MutationNetwork
        net = MutationNetwork(seed=42)
        net.add_node("a", "lab", 300)
        net.add_node("b", "lab", 400)
        net.add_node("c", "api", 500)
        net.add_edge("a", "b", "refactor")
        net.add_edge("b", "c", "split")
        result = net.bfs_reachable("a", max_depth=2)
        assert result["reachable_count"] == 2

    def test_dead_ends(self):
        from lab.experiments.mutation_network import MutationNetwork
        net = MutationNetwork(seed=42)
        net.add_node("a", "lab", 300)
        net.add_node("b", "lab", 400)
        net.add_edge("a", "b", "refactor")
        dead_ends = net.find_dead_ends()
        assert len(dead_ends) == 1
        assert dead_ends[0]["name"] == "b"

    def test_demo(self):
        from lab.experiments.mutation_network import demo
        result = demo()
        assert result["node_count"] > 0


# ─── Entropy Weather tests ───

class TestEntropyWeather:
    def test_measure_pressure(self):
        from lab.experiments.entropy_weather import EntropyWeather
        w = EntropyWeather(seed=42)
        system = w.measure_pressure("test", 10, 500)
        assert system["pressure"] > 0
        assert system["temperature"] >= 0

    def test_generate_fronts(self):
        from lab.experiments.entropy_weather import EntropyWeather
        w = EntropyWeather(seed=42)
        w.measure_pressure("a", 5, 1000)
        w.measure_pressure("b", 20, 200)
        fronts = w.generate_fronts()
        assert isinstance(fronts, list)

    def test_forecast(self):
        from lab.experiments.entropy_weather import EntropyWeather
        w = EntropyWeather(seed=42)
        w.measure_pressure("a", 10, 500)
        forecast = w.forecast_weather(steps=3)
        assert len(forecast) == 3

    def test_report_text(self):
        from lab.experiments.entropy_weather import demo
        result = demo()
        assert "report_text" in result
        assert "ENTROPY WEATHER REPORT" in result["report_text"]


# ─── Fossil Registry tests ───

class TestFossilRegistry:
    def test_demo(self):
        from lab.experiments.fossil_registry import demo
        result = demo()
        assert "total_fossils" in result
        assert "by_type" in result
        assert isinstance(result["fossils"], list)

    def test_scan_empty_functions(self):
        from lab.experiments.fossil_registry import FossilRegistry
        reg = FossilRegistry(seed=42)
        reg.scan_empty_functions("def empty():\n    pass\n\ndef has_body():\n    return 1\n", "test.py")
        assert any(f.fossil_type == "empty_function" for f in reg.fossils)


# ─── Codebase Cartography tests ───

class TestCodebaseCartography:
    def test_demo(self):
        from lab.experiments.codebase_cartography import demo
        result = demo()
        assert result["total_districts"] > 0
        assert result["total_landmarks"] > 0

    def test_navigate(self):
        from lab.experiments.codebase_cartography import CodebaseCartographer
        cart = CodebaseCartographer(seed=42)
        cart.define_districts()
        cart.districts["api"].population = 5
        cart.districts["lab"].population = 10
        cart.roads = [("api", "lab")]
        result = cart.navigate("api", "lab")
        assert result["found"] is True


# ─── Resonance Fingerprint tests ───

class TestResonanceFingerprint:
    def test_fingerprint_file(self):
        from lab.experiments.resonance_fingerprint import ResonanceFingerprinter
        fp = ResonanceFingerprinter(seed=42)
        test_file = ROOT / "lab" / "hex_vm.py"
        if test_file.exists():
            fingerprint = fp.fingerprint_file(test_file)
            assert len(fingerprint.dimensions) > 0
            assert fingerprint.hash

    def test_similarity(self):
        from lab.experiments.resonance_fingerprint import Fingerprint
        fp_a = Fingerprint("a", {"x": 1.0, "y": 0.5})
        fp_b = Fingerprint("b", {"x": 0.9, "y": 0.45})
        sim = fp_a.similarity(fp_b)
        assert 0.9 < sim <= 1.0

    def test_demo(self):
        from lab.experiments.resonance_fingerprint import demo
        result = demo()
        assert "fingerprint_count" in result
        assert "twins" in result
