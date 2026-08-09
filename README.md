# IXPANSION

Small FastAPI and CLI agent scaffold with optional TokenRouter integration. The default
CLI path is offline, so you can run the agent without an API key.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run_agent.py --goal "Explore the mesh"
```

The CLI accepts these options:

| Option | Default | Description |
| --- | --- | --- |
| `--name` | `ixpansion-agent` | Name printed for the agent. |
| `--goal` | `Explore the mesh` | Goal used to build the plan. |
| `--model` | `openai/gpt-4.1` | TokenRouter model override. |
| `--use-tokenrouter` | disabled | Request a TokenRouter summary; requires an API key. |
| `--dashboard` | disabled | Show a compact visual dashboard after the run. |

For example:

```bash
python run_agent.py --name explorer --goal "Inspect the API"
```

For a terminal-friendly visual summary:

```bash
python run_agent.py --goal "Inspect the API" --dashboard
```

## Architecture map

The intended system is organized into five layers:

```text
Operators / daily batch / feature flags / metrics
                    |
Forge agents: PSO / ACO / Island / Federated / 1.3
                    |
Trust: EMA reputation -> VSA routing -> Byzantine votes
                    |
Fabric: mesh_core / CRDT / MPMC ring / gas / shards
                    |
1.0 GA baseline / 1.2 SI toolkit / 1.3 federation
```

Current repository coverage:

| Layer | Available now | Status |
| --- | --- | --- |
| Operators | CLI, dashboard, `make verify` | Implemented |
| Trust | Namespaced trust, EMA updates, idle decay, human gates | Baseline implemented |
| Safety | SQLite audits, dual control, dry-run API automation, URL allowlist | Implemented |
| Forge agents | No PSO, ACO, Island, or Federated executors | Planned |
| Fabric | No mesh core, CRDT, MPMC ring, gas, or shard runtime | Planned |
| SI/federation | No SI toolkit or multi-host transport | Planned |

The current release is a safe scaffold for the operator and trust layers. The
Aether Lattice foundation now composes the offline agent, machine lattice,
trust/audit controls, federation simulator, and swarm metadata behind one
inspectable runtime. Forge, fabric, SI, and federation work should still land
behind tests and `make verify` before being presented as production capabilities.

The local 1.3 federation demonstration is now available as a deterministic,
offline simulator:

```bash
python run_1_3_stack.py
```

It exercises carbon ranking, island-style PSO, lossy in-process transport, VSA
gbest frames, WAN elite migration, and a lattice reuse lane for degraded
machines. The lattice sends only noncritical work to degraded-but-trusted
capacity and quarantines machines below the health, capacity, or trust floor.
Machine telemetry can be refreshed through lattice heartbeats, with an optional
heartbeat timeout that quarantines stale nodes.
It does not open network sockets or
execute production actions; replace the simulated transport and executors before
using it as a multi-host system.

## Local skills

The agent includes offline skills that do not require an API key:

- `summarize`: create a compact first-sentence summary.
- `tasks`: extract tasks from checklist, `TODO:`, and `Task:` lines.
- `check_goal`: check whether a goal has enough detail to act on.
- `usage`: report how often local skills have been used.
- `recycle`: trim old memory and history, then reset skill usage counters. Pass
  a non-negative number to retain that many recent entries; the default is 5.
- `flush_memory`: clear retained memory in the current agent without restarting
  it. Runtime memory and history are bounded to recent entries by default.
- `priority`: classify text as high, medium, or low priority.
- `validate`: check whether text is present and long enough to act on.
- `dedupe`: remove repeated non-empty lines while preserving order.
- `find`: search for a keyword; put the keyword on the first line and content below it.
- `checklist`: format each non-empty line as an unchecked Markdown item.
- `export_memory`: return the agent's current memory as plain text.
- `normalize`: collapse whitespace into one line.
- `outline`: number non-empty input lines.
- `redact`: remove values assigned to common credential fields.
- `sort_tasks`: order task lines by urgency.
- `stats`: report line, word, and character counts.
- `urls`: extract unique HTTP(S) URLs.
- `chunks`: split text into fixed-size chunks; provide the size on the first line.
- `emails`: extract unique email addresses.
- `filename`: sanitize text into a portable filename.
- `frequency`: count words by frequency.
- `groups`: group lines by their first word.
- `hash`: produce a SHA-256 digest without retaining input.
- `kv`: parse `key=value` lines.
- `mentions`: extract unique `@mentions`.
- `status`: count checked and unchecked checklist items.

These skills are available through `Agent.list_skills()` and
`Agent.use_skill(name, text)` for Python callers.
Skill contracts are available through `Agent.describe_skills()`. Memory can be
isolated with `agent.remember(item, namespace="project")`, then exported or
flushed by passing that namespace to the corresponding memory skill.

## Testing and debugging

Run the full dependency-free test suite from the repository root:

```bash
python -m unittest discover -s tests -v
```

In VS Code, select the configured Python interpreter and use **Python Tests:
All Unittest** to debug the suite. **Python Debugger: Current File** also sets
the repository root on `PYTHONPATH`, so tests that import top-level modules such
as `aether_lattice` resolve correctly. Running a test file directly without
that path, for example `python tests/test_aether_lattice.py`, can fail because
Python starts with `tests/` as its import directory.

## TokenRouter integration

Copy `.env.example` to `.env`, then set `TOKENROUTER_API_KEY` to a newly generated key:

```bash
cp .env.example .env
python run_agent.py --goal "Summarize this project" --use-tokenrouter
```

`TOKENROUTER_MODEL` defaults to the premium standard model `openai/gpt-4.1`. Set
`TOKENROUTER_API_URL` to override the OpenAI-compatible endpoint, which is
useful when testing against a compatible service. The client raises a clear
error when the request fails or the response does not contain message content.

The CLI `--model` option takes precedence over `TOKENROUTER_MODEL`. The agent
still runs its local plan and skills without an API key or network access.

`--use-xai` remains accepted as a compatibility alias for
`--use-tokenrouter`.

Never commit `.env` or share an API key.

If a key has ever been pasted into chat, source control, logs, or an issue,
revoke it in the TokenRouter dashboard and create a replacement.

## API

Run the local server:

```bash
uvicorn api.main:app --reload
```

Open [http://127.0.0.1:8000/dashboard](http://127.0.0.1:8000/dashboard) for the
live browser dashboard. It shows health, lattice telemetry, available offline
skills, and includes a small work-allocation control. The raw API remains
available at `/`, `/health`, and the endpoints below.

Available endpoints:

- `GET /` returns `{"service": "ixpansion", "status": "ok"}`.
- `GET /health` returns `{"status": "healthy"}`.
- `GET /aether` returns the unified foundation snapshot across agent, lattice,
  federation, trust, safety, and swarm layers.
- `POST /aether/dispatch` allocates safe capacity, runs the offline agent plan,
  updates node trust, and records an audit event.
- `GET /aether/workflows` lists six token-free automation workflows.
- `POST /aether/workflows/{workflow}` runs `summarize`, `extract_tasks`,
  `make_checklist`, `score_priority`, `normalize_text`, or `dispatch_work`.
- `GET /aether/data` lists reusable data keys; `GET` and `PUT
  /aether/data/{key}` retrieve or store JSON data. Workflow calls with a
  `task_id` automatically save their result under that key.
  Data keys are trimmed, limited to 128 characters, and cannot contain
  whitespace or path separators.
- `GET /skills` lists local skill contracts.
- `POST /skills/{skill}` executes a local skill with `{"text": "..."}`.
- `GET /lattice` reports machine states and active leases.
- `POST /lattice/heartbeat` updates machine telemetry.
- `POST /lattice/allocate` selects a machine and can create a bounded lease.

The skill and lattice API state is process-local and intentionally has no
authentication or persistence claim yet.

Example requests:

```bash
curl http://127.0.0.1:8000/
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/aether
curl http://127.0.0.1:8000/aether/workflows
curl -X PUT http://127.0.0.1:8000/aether/data/project-note \
  -H 'Content-Type: application/json' \
  -d '{"value":{"status":"ready"}}'
curl http://127.0.0.1:8000/aether/data/project-note
curl http://127.0.0.1:8000/skills
curl -X POST http://127.0.0.1:8000/aether/dispatch \
  -H 'Content-Type: application/json' \
  -d '{"task":"Inspect the lattice","task_id":"demo-1"}'
curl -X POST http://127.0.0.1:8000/skills/summarize \
  -H 'Content-Type: application/json' \
  -d '{"text":"Inspect the API. Then run tests."}'
```

FastAPI also exposes interactive API documentation at `/docs` while the local
server is running.

## Automation safety

The dependency-free controls in `security_controls.py` provide a baseline for
automation integrations:

- `AuditStore` persists gate decisions in SQLite with task, tags, trust,
  operator, timestamp, and decision fields.
- `HumanGate` requires a second operator for `PROD_DEPLOY` and `SECRET_ROTATE`.
- Approval rechecks the current namespaced agent trust before allowing a gate.
- `API_AUTOMATION(..., dry_run=True)` validates the URL but never sends a
  request.
- `URLPolicy` rejects hosts that are not explicitly allowlisted.
- `TrustStore` keeps `agent:` and `node:` identities separate and decays idle
  trust after full idle days.

The repository does not currently contain Forge, SI, CRDT, or federation
implementations, so those controls need to be integrated when those systems
are introduced.

## Container swarm demo

The repository includes a small role-based container topology for local testing:

```bash
export SWARM_TOKEN=mysecret
docker compose up --build
docker compose up --build --scale worker=3
```

- `hub` serves health, registration, and status on internal port `8765`.
- `worker` registers a generated node ID with the hub every 10 seconds.
- `panel` serves its health endpoint on internal port `8080`.

The swarm ports are intentionally not published to the host. Only the local
dashboard/API port `8000` needs to be opened for browser access; containers
continue to reach the hub through the internal `hub:8765` service address.

This is an HTTP registration demo, not the planned production WebSocket/RDMA
mesh. `SWARM_TOKEN` is optional for this internal-only local swarm: leave it
unset for trusted local development, or set it to require the
`X-Swarm-Token` header. Add authentication before publishing swarm ports.

## Development checks

```bash
make verify
python -m py_compile agent.py run_agent.py tokenrouter_client.py xai_client.py api/main.py
python -m unittest discover -s tests -v
```
