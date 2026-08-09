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

## Design principles

IXPANSION treats autonomy as a controlled feedback loop rather than an
unbounded agent process:

```text
observe -> classify -> allocate -> act -> audit -> update trust
    ^                                             |
    +------------- bounded, inspectable state ----+
```

The implementation follows four practical computer-science ideas:

- **Deterministic degradation:** offline skills and simulated transport remain
  useful without credentials or network access. External integrations are an
  optional edge, not a prerequisite for the core loop.
- **Trust-aware scheduling:** health, capacity, load, and reputation are part of
  placement. Critical work does not silently fall through to degraded capacity,
  and stale machines can be quarantined instead of receiving new leases.
- **Bounded context:** recycling redacts, deduplicates, chunks, hashes, and
  budgets retained context before retrieval. This keeps memory use and prompt
  size explicit while preserving source-order ties.
- **Evidence before scale:** every new autonomous behavior should have a local
  simulation, a visible snapshot or audit event, and a focused test before it
  grows into a networked or persistent subsystem.

For operators, this produces a simple loop: start offline, inspect `/aether` and
`/lattice`, dispatch a bounded task, then verify the resulting audit and trust
state. The dashboard is deliberately a control surface for that loop, not a
claim that the local process is a secure multi-host deployment.

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
- `POST /aether/recycle` compiles raw text into redacted, deduplicated,
  normalized context with a summary, bounded chunks, SHA-256 source hash, and
  approximate token count. It stores the artifact under `task_id`, or under
  `recycle:latest` when no task ID is supplied. Raw input is not retained.
- `POST /aether/context/{key}/retrieve` selects relevant stored chunks under an
  approximate token budget. Matching terms are ranked first, ties preserve
  source order, and the operation remains offline and process-local.
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
curl -X POST http://127.0.0.1:8000/aether/recycle \
  -H 'Content-Type: application/json' \
  -d '{"text":"API_KEY=placeholder\nKeep this fact.","task_id":"context-1"}'
curl -X POST http://127.0.0.1:8000/aether/context/context-1/retrieve \
  -H 'Content-Type: application/json' \
  -d '{"query":"fact","max_tokens":400}'
curl -X POST http://127.0.0.1:8000/skills/summarize \
  -H 'Content-Type: application/json' \
  -d '{"text":"Inspect the API. Then run tests."}'
```

FastAPI also exposes interactive API documentation at `/docs` while the local
server is running.

### API request shapes

All request bodies are JSON. FastAPI validates required fields and returns a
validation response before the handler runs. Allocation conflicts, unavailable
capacity, and unknown workflows return `409`; unknown skills and missing saved
data return `404`.

Run an offline workflow:

```bash
curl -X POST http://127.0.0.1:8000/aether/workflows/normalize_text \
  -H 'Content-Type: application/json' \
  -d '{"text":"  Inspect   the lattice  ","task_id":"note-1"}'
```

The request supports `text` (required), plus optional `critical`,
`lease_seconds`, `operator`, and `task_id`. The six workflow names are listed
by `GET /aether/workflows`; use the exact returned name in the URL.

Recycle context for later use:

```bash
curl -X POST http://127.0.0.1:8000/aether/recycle \
  -H 'Content-Type: application/json' \
  -d '{"text":"API_KEY=placeholder\nFirst fact.\nFirst fact.","chunk_size":800,"task_id":"context-1"}'
```

The request requires `text` and accepts `chunk_size` from 64 through 4096 and
an optional `task_id`. Input is limited to 50,000 characters. The response
contains `data_key`, `summary`, `chunks`, `source_sha256`, `characters`,
`approximate_tokens`, `chunk_size`, and whether redaction occurred. Recycling
is offline and process-local; it does not send data to TokenRouter or survive
a server restart.

Retrieve only the context needed for a task:

```bash
curl -X POST http://127.0.0.1:8000/aether/context/context-1/retrieve \
  -H 'Content-Type: application/json' \
  -d '{"query":"fact","max_tokens":400}'
```

The retrieval request accepts an optional `query` and `max_tokens` from 1
through 8,000. Its response contains the selected `chunks`, the approximate
tokens returned, and the applied budget. A missing key returns `404`; a key
that does not contain recycled chunks or an invalid budget returns `422`.

Refresh a machine's telemetry before allocating work:

```bash
curl -X POST http://127.0.0.1:8000/lattice/heartbeat \
  -H 'Content-Type: application/json' \
  -d '{"machine_id":"api-healthy-0","load":0.25}'
```

Heartbeat fields other than `machine_id` are optional: `health`, `capacity`,
`trust`, and `load`. Values are applied to the process-local lattice and are
not persisted after a server restart. Allocation accepts `task` (required),
`critical` (default `false`), and optional `lease_seconds`; a lease response
includes `expires_at`.

### Development workflow

Use the dependency-free checks from the repository root:

```bash
make verify
```

The equivalent commands are useful when isolating a failure:

```bash
python -m py_compile agent.py run_agent.py run_1_3_stack.py \
  tokenrouter_client.py xai_client.py api/main.py aether_lattice.py \
  security_controls.py federated_stack.py lattice_stack.py
python -m unittest discover -s tests -v
```

For a focused test run, pass a test module or class to unittest, for example:

```bash
python -m unittest tests.test_api.ApiTests.test_skill_discovery_and_execution -v
```

The test suite uses local process state and does not require a TokenRouter key.
When testing API changes, start the server in one terminal and use `/docs` or
`curl` from another. Stop it with `Ctrl-C`; no background service is required.

### Troubleshooting

- `ModuleNotFoundError`: activate the virtual environment and run
  `python -m pip install -r requirements.txt` from the repository root.
- `Address already in use`: run Uvicorn on another port, for example
  `uvicorn api.main:app --reload --port 8001`, then use that port in requests.
- `TokenRouter API key is required`: omit `--use-tokenrouter` for the offline
  path, or configure `TOKENROUTER_API_KEY` in an untracked `.env` file.
- `409` from allocation or dispatch: inspect `GET /lattice` and
  `GET /aether`; the requested work may be critical, capacity may be leased,
  or all eligible machines may be degraded or quarantined.
- A compose worker cannot register: check `docker compose ps`, then inspect
  `docker compose logs hub worker`. The worker must reach the internal
  `hub:8765` service and use the same `SWARM_TOKEN` as the hub.

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

- `hub` serves health, registration, heartbeat, task leasing, and status on
  internal port `8765`.
- `worker` registers a generated node ID, reports capacity, claims one task at
  a time, and acknowledges completion every 10 seconds.
- `panel` serves its health endpoint on internal port `8080`.

The hub exposes a bounded local task loop. From another compose service, submit
work through the internal `hub:8765` address with a shared token:

```bash
curl -X POST http://hub:8765/tasks \
  -H "X-Swarm-Token: $SWARM_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"task":"Inspect the mesh","task_id":"mesh-1"}'
```

Workers claim queued tasks through `/tasks/claim?node_id=...`. Each claim has
a 30-second lease and must be completed by the assigned node. Repeating a
completion for an already completed task is idempotent. `POST /heartbeat`
accepts `node_id`, `load`, `capacity`, and `health`, each bounded from `0` to
`1`; unhealthy or zero-capacity nodes are reported as degraded and cannot claim
work. Nodes that have not refreshed telemetry for 30 seconds are also rejected.

The swarm ports are intentionally not published to the host. Only the local
dashboard/API port `8000` needs to be opened for browser access; containers
continue to reach the hub through the internal `hub:8765` service address.

This is an HTTP coordination demo, not the planned production WebSocket/RDMA
mesh. Queue state, leases, and node telemetry are process-local and disappear
when the hub restarts. `SWARM_TOKEN` is optional for this internal-only local
swarm: leave it unset for trusted local development, or set it to require the
`X-Swarm-Token` header. Add stronger authentication and durable coordination
before publishing swarm ports or using it across trust boundaries.

## Development checks

```bash
make verify
python -m py_compile agent.py run_agent.py tokenrouter_client.py xai_client.py api/main.py
python -m unittest discover -s tests -v
```
