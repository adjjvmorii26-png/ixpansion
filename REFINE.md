# IXPANSION refined map (IXPANSION/1.5.3-refined)

## Public faces
| Surface | Path |
|---------|------|
| **NEXUS** (centerpiece) | `mesh_public/index.html` |
| VIVARIUM | `mesh_public/vivarium.html` |
| LUMEN | `mesh_public/lumen.html` |

## Code body
| Area | Path |
|------|------|
| Package | `ixpansion/{core,si,security,federation,signal,agent,ops,experimental}/` |
| Workforce / HITL | `ixpansion/security/workforce_pipeline.py`, `vectra_hitl_gate.py` |
| Sandbox lab | `sandbox/` (`run_module`, modules, engine) |
| Idea lattice | `content_output/idea_lattice.json` |

## Verify
```bash
PYTHONPATH=. python3 refine_check.py
# or
make refine
```

## GitHub
Primary: https://github.com/adjjvmorii26-png/ixpansion  
Local 1.5.x artifacts are source of truth for this line.
