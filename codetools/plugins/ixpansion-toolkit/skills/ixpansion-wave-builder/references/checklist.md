# IXpansion Wave Checklist (14 steps)

Follow this exact order. Each step has hidden failure modes that have broken
production before.

## 1. Write the organs
- Create 5-8 `api/<name>.py` files. Each defines `coherence_vitals()`,
  `handler(payload=None, context=None)`, `resonates_with()`.
- First line MUST be `from __future__ import annotations` (with `import`).
- Test locally: `python3 -m py_compile api/<name>.py` and exercise the handler.

## 2. Add intent patterns
- `gateway/intent.py`: add regex rules BEFORE the broad echo/search block
  (anchor: `(r"\b(echo|search|find|look|discover)\b.*\b(\w+)\b", "/echo", ...)`).
- Specific-first ordering matters; late rules shadow broad ones.

## 3. Sync the manifest
- `api/coherence_regulator.py` → `KNOWN_LIVING_MODULES` list (append new names;
  file is one long regex-sorted line — use a script, not hand edits).

## 4. Add API routes to vercel.json
- For each new organ add `{"src": "/<name>", "dest": "/api/<name>"}` at the TOP
  of routes (API before dashboard routes).

## 5. Add slash aliases in api_server.py
- Before the `/cons` dashboard alias. Format:
  ```python
  if path == "/<name>":
      from api.<name> import handler as h
      q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
      return self._json(h(q))
  ```
- `return` MUST be on the next line after the import.

## 6. Add endpoint to api/index.py
- Before the `if path.startswith("/api/"):` catchall, same `q = {}` pattern,
  ending `return h(q)`.

## 7. Bump version + wave
- `api_server.py`: `VERSION`, `WAVE`, `WAVE_NAME`
- `api/organism_ontology.py`: `ORGANISM_VERSION`, `ORGANISM_WAVE`, `ORGANISM_WAVE_NAME`
- `dashboard/shared.js`: `version`, `wave`, `waveName`
- `pyproject.toml`: `version`
- `CITATION.cff`: `version`
- Keep increments as `4.XX.0` and `WAVE = "<n>"` strings in api_server.py but
  ints in organism_ontology.py.

## 8. Create dashboard
- `dashboard/<theme>.html` — monospace terminal aesthetic, `:root` CSS vars,
  include `<script src="/shared.js">`, call `window.IXP.renderIdentity`.
- Add row in `README.md` dashboard table.

## 9. Docs
- `CHANGELOG.md`: new `## [4.XX.0]` entry at top.
- `REVELATIONS.md`: new revelation at top.
- README header version + living-module count.

## 10. Commit + push
```bash
git add -A
git commit -m "Wave N — <Name>\n\n5-8 new organs: ..."
git push origin main
```

## 11. Deploy
```bash
vercel --yes --prod --token <VCP_TOKEN>
```

## 12. Verify
```bash
curl -s https://ixpansion.vercel.app/health
curl -s https://ixpansion.vercel.app/api/<new_organ>
curl -s -o /dev/null -w "%{http_code}" https://ixpansion.vercel.app/<dashboard>
```

## Critical bugs — check every time
- `from __future__ annotations` (missing `import`) → SyntaxError, deploy fails.
- `str.strip("/api/")` mangles names → use `removeprefix()`.
- Query params lost on custom routes → use the explicit `q = {}` parse.
- `return` missing after route import → 500s on that route.
- Vercel read-only FS → state must fall back to in-memory.
- Manifest out of sync → regulator health drops / modules vanish from lists.
