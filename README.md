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
| `--use-tokenrouter` | disabled | Request a TokenRouter summary; requires an API key. |

For example:

```bash
python run_agent.py --name explorer --goal "Inspect the API"
```

## Local skills

The agent includes offline skills that do not require an API key:

- `summarize`: create a compact first-sentence summary.
- `tasks`: extract tasks from checklist, `TODO:`, and `Task:` lines.
- `check_goal`: check whether a goal has enough detail to act on.
- `usage`: report how often local skills have been used.
- `recycle`: trim old memory and history, then reset skill usage counters. Pass
	a non-negative number to retain that many recent entries; the default is 5.
- `priority`: classify text as high, medium, or low priority.
- `validate`: check whether text is present and long enough to act on.
- `dedupe`: remove repeated non-empty lines while preserving order.
- `find`: search for a keyword; put the keyword on the first line and content below it.
- `checklist`: format each non-empty line as an unchecked Markdown item.
- `export_memory`: return the agent's current memory as plain text.

These skills are available through `Agent.list_skills()` and
`Agent.use_skill(name, text)` for Python callers.

## TokenRouter integration

Copy `.env.example` to `.env`, then set `TOKENROUTER_API_KEY` to a newly generated key:

```bash
cp .env.example .env
python run_agent.py --goal "Summarize this project" --use-tokenrouter
```

`TOKENROUTER_MODEL` defaults to `moonshotai/kimi-k3-free`. Set
`TOKENROUTER_API_URL` to override the OpenAI-compatible endpoint, which is
useful when testing against a compatible service. The client raises a clear
error when the request fails or the response does not contain message content.

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

Available endpoints:

- `GET /` returns `{"service": "ixpansion", "status": "ok"}`.
- `GET /health` returns `{"status": "healthy"}`.

Example requests:

```bash
curl http://127.0.0.1:8000/
curl http://127.0.0.1:8000/health
```

FastAPI also exposes interactive API documentation at `/docs` while the local
server is running.

## Development checks

```bash
python -m py_compile agent.py run_agent.py tokenrouter_client.py xai_client.py api/main.py
python -m unittest discover -s tests -v
```
