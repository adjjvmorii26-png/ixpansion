# IXPANSION

Small FastAPI and CLI agent scaffold with optional xAI integration.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run_agent.py --goal "Explore the mesh"
```

The default CLI path is offline and does not require an API key.

## xAI integration

Copy `.env.example` to `.env`, then set `XAI_API_KEY` to a newly generated key:

```bash
cp .env.example .env
python run_agent.py --goal "Summarize this project" --use-xai
```

Never commit `.env` or share an API key. `XAI_MODEL` defaults to `grok-3-mini`,
and `XAI_API_URL` can override the OpenAI-compatible endpoint for testing.

If a key has ever been pasted into chat, source control, logs, or an issue,
revoke it in the xAI dashboard and create a replacement.

## API

Run the local server:

```bash
uvicorn api.main:app --reload
```

Available endpoints:

- `GET /` returns service metadata.
- `GET /health` returns a health status.

## Development checks

```bash
python -m py_compile agent.py run_agent.py xai_client.py api/main.py
python -m unittest discover -s tests -v
```
