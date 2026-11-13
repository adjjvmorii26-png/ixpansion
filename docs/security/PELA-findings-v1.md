# PELA — Evidence-Backed Findings

**Schema:** `pela.findings.v1`  
**Status:** Initial static-source findings; runtime reproduction not yet performed  
**Target source snapshot:** `45b0922a003cee7a205f973b7aa95434119ca6a4`  
**Audit contract:** [PELA.md](./PELA.md)

## EBF-0001 — Unescaped ledger data is rendered into Chronicle HTML

- **Severity:** High (provisional; depends on ledger write access and how the generated HTML is consumed)
- **Confidence:** Confirmed for the unsafe source path; exploitability and downstream exposure remain unverified
- **Category:** Output encoding / trust-boundary failure
- **Affected source:** `lab/chronicle_weaver.py`, `_entry_summary`, `_label_for`, `_render`, `weave_chronicle`
- **Evidence:** [source at audited commit](https://github.com/adjjvmorii26-png/ixpansion/blob/45b0922a003cee7a205f973b7aa95434119ca6a4/lab/chronicle_weaver.py)
- **Test evidence:** Existing `lab/tests/test_chronicle_weaver.py` covers ordinary output, deterministic output, and CLI behavior; inspected tests do not cover hostile HTML payloads or invalid-ledger render policy.

### Observed source behavior

1. `weave_chronicle()` calls `verify_jsonl(path)` and then separately calls `read_jsonl(path)`.
2. It passes the returned entries into the timeline and HTML renderer regardless of `audit["ok"]`.
3. `_render()` interpolates values derived from ledger records directly into HTML text contexts, including timestamp, label/type, ref, and summary, without HTML escaping.
4. When enabled, the function persists the report and can write the HTML to a caller-supplied output path even if the audit reports failure.

### Impact assessment

If an attacker or untrusted process can modify a ledger and a user opens the generated HTML in a browser, a crafted record may inject markup or script into the report. The integrity verifier detects some tampering, but the current rendering path does not use a failed audit to block or safely quarantine those values. This is a trust-boundary/output-encoding issue; it is not yet demonstrated as a remotely reachable exploit.

### Recommended remediation (separate application-hardening change)

- HTML-escape every untrusted value at the final HTML text-context sink; handle attribute and URL contexts with context-appropriate validation/encoding.
- Keep the audit status explicit in the report and do not represent invalid ledger entries as verified evidence.
- Prefer fail-closed rendering for decision/trust-bearing reports. If diagnostic rendering of corrupted data is a required feature, render only safely escaped values and add an unmistakable untrusted/invalid banner.
- Avoid a verify-then-reread race where possible: verify and render the same captured bytes/records, or bind the read snapshot to a digest and ensure the report records that exact snapshot.
- Add regression tests with payloads such as `<script>`, `<img onerror=...>`, quotes, and malformed fields; assert they appear as escaped text and that a tampered ledger cannot produce a trusted/normal report.

### Required validation before closure

- Reproduce the unsafe output using a disposable runtime directory and a malicious fixture record; do not use production or tracked data.
- Test both intact and tampered hash-chained ledgers.
- Check whether generated HTML is served by any endpoint or consumed automatically; until traced, local file-open exposure is the established scenario.
- Re-run targeted tests in an isolated worktree because repository test setup may reset tracked `data/` paths.

### PELA trust-transition record

| From | To / use | Check performed | Assessment |
|---|---|---|---|
| Persisted JSONL record | HTML report content | Integrity audit is computed, but its result does not gate the rendering path; values are not escaped | **Needs review / unsafe source behavior confirmed** |
| HTML report | User/browser interpretation | No output-encoding boundary visible in `_render` | **Unverified downstream exposure** |

## EBF-0002 — SQLite mutation-log identity and read lineage remain unresolved

- **Severity:** Informational / coverage gap
- **Confidence:** Confirmed gap in current static inventory, not a confirmed defect
- **Affected source:** `api/emergent_skills.py::_log_module_mutation`
- **Evidence:** [source](https://github.com/adjjvmorii26-png/ixpansion/blob/45b0922a003cee7a205f973b7aa95434119ca6a4/api/emergent_skills.py)

The writer inserts into `data/memories_1.sqlite` / `module_dreams` and returns the floating-point timestamp as `entry_id`, although the table's primary key is a separate auto-incrementing `id`. Focused repository searches found no other references to `module_dreams` or `memories_1.sqlite`; this does not exclude dynamic queries, external consumers, or unindexed references.

Next evidence needed: trace all call sites of `_log_module_mutation`, confirm whether its return value is consumed, identify actual readers, and test distinct same-payload observations under controlled timestamps. Do not change the return contract until consumer compatibility is understood.

## Limitations

- No application code was changed.
- No tests were run; the finding is based on static source inspection.
- The severity label is provisional pending data-source reachability and report-consumer tracing.
- This file records audit evidence only; remediation belongs in a separately reviewed application-hardening change.
