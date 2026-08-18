# Grok / xAI API Integration

## Setup
1. Account + key: https://console.x.ai (API Keys)
2. Export:
```bash
export XAI_API_KEY="your_key"
# optional
export XAI_MODEL="grok-4.5"          # or grok-4-fast-reasoning, etc.
export XAI_API_BASE="https://api.x.ai/v1"
```

## Official surface
- Base: `https://api.x.ai/v1`
- Auth: `Authorization: Bearer $XAI_API_KEY`
- OpenAI-compatible Chat Completions + Responses API
- Docs: https://docs.x.ai/developers/quickstart
- Models: `grok-4.5`, fast variants, etc. (see console for your team)

## Swarm wiring
```bash
python grok_swarm_client.py          # status / smoke
```

Capability card registers: `llm_reason`, `grok`, `xai`, `synthesize`, `narrate`, …

### Suggested call sites
| Swarm module | Grok role |
|--------------|-----------|
| `auto_content_engine` | Narrate lattice + genetic results for @adjjv |
| `youtube_publish_pipeline` | Title/description polish |
| `genetic_sandbox` | Suggest AST-safe mutations (`evolve_hint`) |
| `neural_symbolic_core` | Fallback when local intent confidence is low |
| `cross_node_handoff_secure` | Remote capability `synthesize` on a worker with key |

### OpenAI SDK pattern
```python
from openai import OpenAI
client = OpenAI(api_key=os.environ["XAI_API_KEY"], base_url="https://api.x.ai/v1")
r = client.chat.completions.create(model="grok-4.5", messages=[...])
```

### Native SDK
```bash
pip install xai-sdk
```

## Security
- Never commit `XAI_API_KEY`
- Prefer worker-side keys only on trusted nodes (ledger debit for paid calls)
- OCI sandbox still applies to any code Grok proposes before hot-swap
- 
