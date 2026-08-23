from engine.vm.core import EngineVM


def run(source: str) -> list[object]:
    return EngineVM(source).outputs
