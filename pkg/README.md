# pkg/ — IXPANSION package (submodule-safe)

Remote `ixpansion/` path is a **git submodule**. Local package code ships under **`pkg/`** to avoid the 409 conflict.

```
pkg/
  core/
  security/
  signal/
  agent/
  si/
  ops/
  federation/
  experimental/
```

Import (with PYTHONPATH including pkg parent):
```python
from pkg.security.workforce_pipeline import WorkforcePipeline
# or symlink/copy to ixpansion/ when submodule is removed
```
