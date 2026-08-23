from pathlib import Path

TEMPLATE = 'from agents.base import Agent\n\n\nclass {class_name}(Agent):\n    name = "{name}"\n    temperament = "experimental"\n'


def generate(name: str, destination: Path) -> Path:
    class_name = "".join(part.capitalize() for part in name.split("_")) + "Agent"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(TEMPLATE.format(name=name, class_name=class_name), encoding="utf-8")
    return destination
