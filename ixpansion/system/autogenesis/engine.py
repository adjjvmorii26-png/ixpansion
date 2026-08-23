from pathlib import Path
from tools.generators.module_gen import generate


def grow(name: str, destination: Path) -> Path:
    return generate(name, destination)
