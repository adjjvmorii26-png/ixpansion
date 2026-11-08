# Compact context artifacts

**Rule:** agents load `pack(budget)`, never chat history.

```python
from context.compact import load_jsonl, pack
print(pack(load_jsonl("context/ledger.jsonl"), budget_tokens=2000))
```

Kinds: `seed` · `contract` · `receipt` · `pulse` · `pointer` · `residue`
