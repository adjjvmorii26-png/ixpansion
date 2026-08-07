---
name: xai-integration-maintainer
description: 'Maintain the optional xAI integration in IXPANSION. Use when changing API keys, models, endpoints, request payloads, timeout handling, response parsing, or network error behavior.'
argument-hint: '[xAI integration task]'
user-invocable: true
---

# xAI Integration Maintainer

Keep the xAI path optional, configurable, and safe to test offline.

## Workflow

1. Inspect `agent.py`, `xai_client.py`, `.env.example`, and related tests.
2. Confirm configuration precedence and safe defaults before changing request code.
3. Never print, commit, or assert real credentials.
4. Mock `urllib.request.urlopen` in tests and cover HTTP, connection, timeout, malformed JSON, and malformed response cases when relevant.
5. Preserve `XAI_MODEL` and `XAI_API_URL` overrides unless the change explicitly revises the contract.
6. Use `XAIClientError` for request or response failures and give callers actionable context.
7. Run:

```bash
python -m unittest tests.test_agent -v
```

The offline CLI must continue to work without an API key.
