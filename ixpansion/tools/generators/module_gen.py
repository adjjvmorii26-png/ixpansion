from pathlib import Path

TEMPLATE = '"""Generated module {name}."""\n\nclass {class_name}:\n    def __init__(self) -> None:\n        self.active = True\n'


def generate(name: str, destination: Path) -> Path:
    class_name = "".join(part.capitalize() for part in name.split("_"))
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(TEMPLATE.format(name=name, class_name=class_name), encoding="utf-8")
    return destination
