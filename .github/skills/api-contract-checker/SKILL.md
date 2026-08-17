---
name: api-contract-checker
description: 'Verify and document the IXPANSION FastAPI contract. Use when changing endpoints, response payloads, status codes, health checks, OpenAPI behavior, or local server instructions.'
argument-hint: '[endpoint or API behavior]'
user-invocable: true
---

# API Contract Checker

Treat route functions, FastAPI metadata, and tests as the API contract.

## Workflow

1. Inspect `api/main.py` and the nearest API tests.
2. Record method, path, response shape, status code, and failure behavior.
3. Change the smallest route or schema surface needed.
4. Verify routes with `TestClient`; do not require a running server for unit tests.
5. For local smoke checks, run `uvicorn api.main:app --reload` and exercise `/`, `/health`, and `/docs`.
6. Update README examples whenever an endpoint or payload changes.
7. Run:

```bash
python -m unittest tests.test_api -v
```

## Contract Rules

- Keep health responses simple and machine-readable.
- Avoid documenting routes that do not exist.
- Test exact JSON payloads for stable endpoints.
- Do not add authentication or persistence claims without implementation.
