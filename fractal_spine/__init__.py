"""PK_SUITE_v01 — The Five Modules of the Fractal Spine"""
from .spine_core import handler as spine_handler
from .quantum_slots import handler as quantum_handler
from .memory_forge import handler as memory_handler
from .bio_mesh import handler as bio_handler
from .temporal_engine import handler as temporal_handler

SUITES = {
    "PK01": {"name": "FRACTAL_RELAY_SPINE", "handler": spine_handler},
    "PK02": {"name": "QUANTUM_SLOT_MATRIX", "handler": quantum_handler},
    "PK03": {"name": "HEX_LATTICE_MEMORY_FORGE", "handler": memory_handler},
    "PK04": {"name": "BIO_SYNTHETIC_DIRECTORY_MESH", "handler": bio_handler},
    "PK05": {"name": "TEMPORAL_ORBIT_ENGINE", "handler": temporal_handler},
}
