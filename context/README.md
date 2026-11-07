# Compact context artifacts

**Rule:** agents load `pack(budget)`, never chat history.

## Kinds

| kind | role |
|------|------|
| `seed` | permanent intent |
| `contract` | boundary / deny rules |
| `receipt` | one completed action |
| `pulse` | short-lived status |
| `pointer` | link to heavy state |
| `residue` | failure → lesson |

## Usage

```python
from context.compact import load_jsonl, pack, append_jsonl, promote_residue_to_seed

rows = load_jsonl("context/ledger.jsonl")
print(pack(rows, budget_tokens=2000))
```

```bash
python -m context.compact
```

## Operators

- `validate` / `bind` — schema + id conflict fail-closed
- `forget` — TTL expiry
- `promote_residue_to_seed` — lesson becomes permanent
- `pack` — priority order, hard char budget

No network. No secrets in ledger lines.
