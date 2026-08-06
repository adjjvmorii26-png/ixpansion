# ixpansion

Sovereign multi-agent mesh: simulate · verify · evolve · publish.

## Quick start

```bash
# Regression (core health)
python run_regression.py

# Intent → primitive compiler
python mesh_compiler.py

# Full publish package
python swarm.py --publish-package

# Daemon once (breakthrough → YouTube bundle)
python swarm_daemon.py --once

# Chaos drill
python chaos_mesh_drill.py
```

## Architecture layers

| Layer | Modules |
|-------|---------|
| Consensus | `raft_consensus.py`, `swarm_crdt.py`, `swarm_merkle_crdt.py` |
| Security | `node_auth.py`, `mesh_tunnel.py`, `task_verifiability.py`, `oci_sandbox.py` |
| Cognition | `vsa_memory.py`, `vsa_semantic_router.py`, `neural_symbolic_core.py` |
| Execution | `spatial_shard.py`, `genetic_sandbox.py`, `closed_loop_physics.py`, `ixpansion_executor.py` |
| Compiler | `mesh_compiler.py` (AST → IR → gas → receipt → dry-run) |
| Orchestration | `task_dag.py`, `swarm_daemon.py`, `swarm.py` |
| Content | `auto_content_engine.py`, `youtube_publish_pipeline.py`, `grok_swarm_client.py` |
| Ops | `chaos_mesh_drill.py`, `cluster_operator.py`, `reputation_ledger.py`, `run_regression.py` |

## Brand

See `BRANDING.md`. Channel target: **@adjjv** · series *IXPANSION Logs*.

## xAI / Grok

```bash
export XAI_API_KEY=...
python grok_swarm_client.py
```

Details: `XAI_INTEGRATION.md`

## Safety model

- AST sandbox + OCI process isolation for evolved code
- HMAC compilation receipts + policy hash grace
- Shadow CoW staging (no durable I/O on abort)
- Byzantine VSA isolation + Raft quorum
- 
