# PELA — Initial Persistence Surface Inventory

**Schema:** `pela.inventory.v1`  
**Status:** Initial, partial, static-source inventory  
**Repository:** `adjjvmorii26-png/ixpansion`  
**Target:** default branch snapshot inspected during this audit; confirm commit SHA before treating this inventory as a release artifact.

> This document is not a complete repository inventory. These records are concrete source-level leads. Reader coverage, runtime behavior, and repository-wide write coverage remain open.

## Inventory summary

| ID | Component | Storage / side effect | Initial assessment |
|---|---|---|---|
| PS-0001 | Emergent Skills mutation log | SQLite: `data/memories_1.sqlite` | Writer confirmed by source; readers unknown |
| PS-0002 | Veinbed state | JSON file, GitHub Contents API, `/tmp` fallback | Multiple possible state locations; reconciliation unknown |
| PS-0003 | Ouroboros ledger | JSON file, `/tmp` fallback | Hash-chain timestamp consistency needs test |
| PS-0004 | Runtime Vault JSON | Atomic file replacement | Atomic visibility implemented; durability/parent directory and consumer trust require review |
| PS-0005 | Runtime Vault JSONL ledger | Append-only JSONL with hash-chain helper | Duplicate function definition; malformed-record behavior needs tests |
| PS-0006 | Pytest data reset | Git working-tree mutation | Potentially destructive test side effect; isolate before test execution |

## PS-0001 — Emergent Skills mutation log

```yaml
schema_version: "pela.inventory.v1"
component:
  id: "PS-0001"
  name: "emergent_skills_mutation_log"
  module: "api.emergent_skills"
  storage_type: "sqlite"
  location: "data/memories_1.sqlite"
  owners: ["api.emergent_skills._log_module_mutation"]
writes:
  - interface: "_log_module_mutation"
    source: "api/emergent_skills.py:487-519"
    data_types: ["module mutation event", "organism state snapshot"]
reads: []
trust_dimensions:
  origin: "unknown beyond supplied module and runtime state"
  storage: "persisted"
  integrity: "not checked by the writer"
  freshness: "timestamp stored; consumer freshness policy unknown"
  verification: "unverified by this write path"
  authority: "not established"
provenance: "static_inspection"
confidence: "confirmed"
```

**Source:** [api/emergent_skills.py](https://github.com/adjjvmorii26-png/ixpansion/blob/45b0922a003cee7a205f973b7aa95434119ca6a4/api/emergent_skills.py#L487-L519)

Observed behavior: the function creates the `module_dreams` table if absent, inserts timestamp, module name, JSON-serialized changes, and JSON-serialized organism-state snapshot, commits, and closes the connection.

Open questions:
- Is `module_dreams` read anywhere else in the repository?
- Does `entry_id` (returned as the timestamp) identify a row, or only approximate its event time?
- What does the exception fallback actually persist? The exception branch returns a fallback-shaped status, but this function's shown branch does not itself write a local fallback record.
- Are SQLite connection lifecycle, locking, busy timeout, schema migrations, and duplicate observation identity covered by tests?

## PS-0002 — Veinbed state

```yaml
schema_version: "pela.inventory.v1"
component:
  id: "PS-0002"
  name: "veinbed_state"
  module: "api.veinbed"
  storage_type: "json"
  location: "data/veinbed.json; /tmp/veinbed.json fallback; GitHub Contents API when configured"
  owners: ["_load", "_save", "_state_read", "_state_write"]
writes:
  - interface: "_save"
    source: "api/veinbed.py:48-65"
    data_types: ["veinbed state object"]
  - interface: "_state_write"
    source: "api/veinbed.py:92 onward"
    data_types: ["veinbed state object"]
reads:
  - interface: "_load"
    source: "api/veinbed.py:38-46"
    consumers: ["_state_read"]
trust_dimensions:
  origin: "unknown"
  storage: "persisted; may resolve to GitHub or local fallback"
  integrity: "not established by path selection alone"
  freshness: "not established"
  verification: "unknown"
  authority: "ambiguous while multiple backends/fallbacks are possible"
provenance: "static_inspection"
confidence: "confirmed"
```

**Source:** [api/veinbed.py](https://github.com/adjjvmorii26-png/ixpansion/blob/45b0922a003cee7a205f973b7aa95434119ca6a4/api/veinbed.py#L38-L110)

Observed behavior: loading tries the requested path and then a `/tmp` path with the same basename. State read/write behavior may use GitHub Contents API when a token is configured, or local JSON otherwise.

Risk to investigate: the actual authoritative location may depend on environment and API success. Establish explicit backend selection, provenance, fallback policy, and reconciliation semantics before describing any one copy as authoritative.

## PS-0003 — Ouroboros ledger

```yaml
schema_version: "pela.inventory.v1"
component:
  id: "PS-0003"
  name: "ouroboros_ledger"
  module: "api.ouroboros"
  storage_type: "json"
  location: "data/ouroboros.json; /tmp/ouroboros.json fallback"
  owners: ["seal", "chain", "_load", "_save"]
writes:
  - interface: "seal"
    source: "api/ouroboros.py:46-68"
    data_types: ["seal block", "hash chain"]
reads:
  - interface: "chain"
    source: "api/ouroboros.py:71-88"
    consumers: ["handler /chain"]
trust_dimensions:
  origin: "commit SHA is recorded but not independently authenticated here"
  storage: "persisted"
  integrity: "hash chain attempted; consistency needs regression test"
  freshness: "sealed_at recorded; live-state semantics not established"
  verification: "chain() attempts verification"
  authority: "not established"
provenance: "static_inspection"
confidence: "confirmed"
```

**Source:** [api/ouroboros.py](https://github.com/adjjvmorii26-png/ixpansion/blob/45b0922a003cee7a205f973b7aa95434119ca6a4/api/ouroboros.py#L46-L88)

**Specific test candidate:** `seal()` computes the hash input using `time.time():.0f` but stores a separate `time.time()` value in `sealed_at`; `chain()` recomputes using `int(sealed_at)`. These are not equivalent timestamp operations in general. A deterministic test should inject a clock and test values on both sides of a second boundary. Until that test is run, label the resulting validation failure as a **hypothesis**, not a confirmed runtime defect.

Other questions: malformed block schemas can raise during verification; the `/tmp` fallback can make state location ambiguous; chain truncation and `total` semantics should be tested.

## PS-0004 — Runtime Vault JSON

```yaml
schema_version: "pela.inventory.v1"
component:
  id: "PS-0004"
  name: "runtime_vault_json"
  module: "lab.runtime_vault"
  storage_type: "filesystem_json"
  location: ".runtime/lab by default; override via NEXUS_LAB_RUNTIME"
  owners: ["write_json", "read_json", "path", "state_path", "ledger_path", "report_path"]
writes:
  - interface: "write_json"
    source: "lab/runtime_vault.py:38-62"
    data_types: ["JSON-serializable payload"]
reads:
  - interface: "read_json"
    source: "lab/runtime_vault.py:30-36"
    consumers: ["multiple lab modules; call graph incomplete"]
trust_dimensions:
  origin: "not inherent in JSON serialization"
  storage: "persisted"
  integrity: "not inherent in atomic replacement"
  freshness: "caller-specific"
  verification: "caller-specific"
  authority: "caller-specific"
provenance: "static_inspection"
confidence: "confirmed"
```

**Source:** [lab/runtime_vault.py](https://github.com/adjjvmorii26-png/ixpansion/blob/45b0922a003cee7a205f973b7aa95434119ca6a4/lab/runtime_vault.py#L15-L62)

Observed behavior: writes use a temporary file in the destination directory, flush and fsync the file, then call `os.replace`. This supports atomic replacement semantics for readers on typical local filesystems; it does not by itself prove authenticity, freshness, or full crash durability (for example, parent-directory fsync is not shown).

## PS-0005 — Runtime Vault JSONL ledger

```yaml
schema_version: "pela.inventory.v1"
component:
  id: "PS-0005"
  name: "runtime_vault_jsonl"
  module: "lab.runtime_vault"
  storage_type: "jsonl_hash_chain"
  location: "caller-selected path, commonly under runtime vault ledgers"
  owners: ["append_jsonl", "read_jsonl", "verify_jsonl"]
writes:
  - interface: "append_jsonl"
    source: "lab/runtime_vault.py:124-157"
    data_types: ["hash-chained JSON object"]
reads:
  - interface: "read_jsonl"
    source: "lab/runtime_vault.py:66-82"
    consumers: ["multiple lab modules; call graph incomplete"]
  - interface: "verify_jsonl"
    source: "lab/runtime_vault.py:159-215"
    consumers: ["multiple lab modules; call graph incomplete"]
trust_dimensions:
  origin: "not authenticated by the hash chain alone"
  storage: "persisted"
  integrity: "verifier checks sequence, link, and entry hash"
  freshness: "not inherently checked"
  verification: "explicit verifier exists; caller enforcement unknown"
  authority: "not established"
provenance: "static_inspection"
confidence: "confirmed"
```

**Source:** [lab/runtime_vault.py](https://github.com/adjjvmorii26-png/ixpansion/blob/45b0922a003cee7a205f973b7aa95434119ca6a4/lab/runtime_vault.py#L66-L215)

Review notes:
- `append_jsonl` is defined twice. The later definition overrides the earlier one at import time; inventory the effective definition and consider removing the dead one after tests.
- `read_jsonl` skips malformed JSON lines and non-dictionary values. This convenience reader must not be used as an integrity verifier.
- The chained append scans past malformed lines to locate a previous dictionary. A later append can therefore extend a chain without first refusing a corrupted ledger.
- `verify_jsonl` converts the stored sequence using `int(...)`; malformed values can raise instead of returning a structured verification failure. Test the public contract against invalid types and truncated/tampered records.
- Hash chaining detects some changes relative to the chain, but does not authenticate the writer or prove the recorded claim is true.

## PS-0006 — Pytest data reset side effect

```yaml
schema_version: "pela.inventory.v1"
component:
  id: "PS-0006"
  name: "pytest_tracked_data_reset"
  module: "tests.conftest"
  storage_type: "git_worktree_mutation"
  location: "tracked files under data/"
  owners: ["pytest_configure"]
writes:
  - interface: "subprocess git checkout -- data/"
    source: "tests/conftest.py:14-21"
    data_types: ["working-tree files under data/"]
reads: []
trust_dimensions:
  origin: "git index/HEAD baseline"
  storage: "working-tree mutation"
  integrity: "not applicable"
  freshness: "not applicable"
  verification: "not applicable"
  authority: "test fixture assumes committed baseline should replace working-tree state"
provenance: "static_inspection"
confidence: "confirmed"
```

**Source:** [tests/conftest.py](https://github.com/adjjvmorii26-png/ixpansion/blob/45b0922a003cee7a205d0c2ea81a36b3?plain=1#L1-L22)

The fixture runs `git checkout -- data/` during pytest configuration and discards tracked working-tree changes under that path. Do not run the suite in a workspace containing uncommitted changes under `data/`. Safer approaches include a disposable worktree or isolated test data root, followed by an explicit test verifying the fixture never mutates the developer's tracked data.

## Immediate next searches

1. Search all source and tests for `module_dreams`, `memories_1.sqlite`, and `_log_module_mutation`; identify every reader and call site.
2. Enumerate `read_jsonl`, `verify_jsonl`, and `append_jsonl` callers; check whether every security-sensitive consumer requires a successful verification result.
3. Trace `_state_read` and `_state_write` call sites for Veinbed; identify which backend wins under token/API errors.
4. Add deterministic tests for Ouroboros timestamp reconstruction and malformed ledger records.
5. Inspect all direct file writes and database APIs repository-wide before claiming inventory coverage.

## Completion status

- [x] Initial persistence surfaces recorded
- [x] Known fallback and test side-effect paths recorded
- [x] Trust dimensions kept separate
- [ ] Complete repository-wide write inventory
- [ ] Complete reader/consumer lineage
- [ ] Trust-transition register populated from call sites
- [ ] Regression tests executed in a safe isolated workspace
- [ ] Runtime behavior verified and findings reproduced
