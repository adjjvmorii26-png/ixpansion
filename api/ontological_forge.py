"""Wave 129 — Ontological Forge.

Forges new categories of being — creates novel ontological classes
that didn't exist before, bridging gaps in the system's understanding
of what types of things can exist.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class OntologicalClass:
    """A forged category of being."""

    def __init__(self, name: str, parent: Optional[str] = None):
        self.name = name
        self.parent = parent
        self.properties: List[str] = []
        self.instances: int = 0
        self.created = time.time()
        self.id = hashlib.sha256(f"onto:{name}".encode()).hexdigest()[:10]

    def add_property(self, prop: str) -> None:
        self.properties.append(prop)

    def spawn(self) -> int:
        self.instances += 1
        return self.instances

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "parent": self.parent,
                "properties": self.properties, "instances": self.instances}


class OntologicalForge:
    """Forges new categories of being."""

    def __init__(self):
        self._classes: Dict[str, OntologicalClass] = {}

    def forge(self, name: str, parent: Optional[str] = None) -> OntologicalClass:
        cls = OntologicalClass(name, parent)
        self._classes[cls.id] = cls
        return cls

    def add_property(self, class_id: str, prop: str) -> bool:
        cls = self._classes.get(class_id)
        if cls:
            cls.add_property(prop)
            return True
        return False

    def get_class(self, class_id: str) -> Optional[Dict[str, Any]]:
        cls = self._classes.get(class_id)
        return cls.to_dict() if cls else None

    def ontology_tree(self) -> List[Dict[str, Any]]:
        return [c.to_dict() for c in self._classes.values()]

    def status(self) -> Dict[str, Any]:
        return {"total_classes": len(self._classes),
                "total_instances": sum(c.instances for c in self._classes.values())}
