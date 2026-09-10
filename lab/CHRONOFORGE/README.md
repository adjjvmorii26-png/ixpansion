# CHRONOFORGE

Long-horizon specification stack for IXPANSION organism base.

```
000_ROOT_SPEC/     charter, ontology, epochs, threat model, invariants.hex
010_PROTOCOLS/     identity, storage, messaging, governance (+ ETP-1)
020_CRYPTO_SUITES/ E1 · E2 · E∞
030_ARCHIVE_LAYERS/
040_RUNTIME_CORES/
050_GOVERNANCE/
060_TOOLING_SHIMS/
070_TESTAMENTS/
runtime/           cf_portal.py
```

```bash
python lab/CHRONOFORGE/runtime/cf_portal.py invariants
python lab/CHRONOFORGE/runtime/cf_portal.py transition-plan E2
python lab/CHRONOFORGE/runtime/cf_portal.py boot
```
