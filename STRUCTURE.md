# IXPANSION source layout

```
ixpansion/
  core/          mesh, CRDT, VSA, trust, status
  si/            PSO, ACO, islands, federated SI
  security/      Vectra HITL, workforce, TEE, Byzantine
  federation/    transport, carbon, WAN migration
  signal/        LUMEN, metrics, telemetry
  agent/         tool registry, agent runner, task assistant, swarm
  ops/           chaos, tests, snapshots, watchdog
  experimental/  omega / research modules + living toys
docs/
  reports/ notes/ roadmap/ releases/
mesh_public/     LUMEN + VIVARIUM + NEXUS static site
sandbox/         local lab modules
content_output/  runtime artifacts
```

Prefer: `from ixpansion.core.mesh_core import IXPANSIONMesh`
