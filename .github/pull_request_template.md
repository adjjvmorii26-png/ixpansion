## Description

<!-- What does this PR do? -->

## Which layer?

- [ ] Core (agents, experiments, sandbox)
- [ ] Revenue (billing, crypto, marketplace)
- [ ] Intelligence (cognitive, neural, memory)
- [ ] Experimental (new wave modules)
- [ ] Infrastructure (gateway, auth, events)
- [ ] Tests
- [ ] Documentation / Config

## Experimental justification

<!-- Why is this system interesting? What emergent behaviour might it produce? -->

## Testing

- [ ] All existing tests pass (`python3 -m pytest tests/ -q`)
- [ ] New modules have handler functions
- [ ] Vercel routes added for new modules
- [ ] CHANGELOG.md updated

## Library Core integrity contract

### Entries touched
- IDs and shelves:

### Evidence changes
- `ENTRY-ID`: oldstate → newstate — justification and evidence reference
- If none, write "None".

### New contradictions
- Frontier ID, entries, dimension, and proposed follow-up:
- If none, write "None".

### Validator output summary
- Command / run link:
- Result:
- If not yet run, say so explicitly.

### Integrity checklist
- [ ] IDs are new or already reserved; no ID is reused.
- [ ] Every evidence-state transition has complete lineage metadata.
- [ ] Each PR advances an entry by no more than one evidence level.
- [ ] Relationship references resolve to versioned entries.
- [ ] Contradictions are represented in the Contradiction Atlas and have follow-ups.
- [ ] Focused regression tests pass.
