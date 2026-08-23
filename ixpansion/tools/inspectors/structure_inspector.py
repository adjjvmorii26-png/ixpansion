from pathlib import Path


def inspect(root: str | Path) -> dict[str, int]:
    base = Path(root)
    return {
        "python_files": len(list(base.rglob("*.py"))),
        "directories": len([item for item in base.rglob("*") if item.is_dir()]),
    }
