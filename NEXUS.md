# NEXUS — centerpiece interface

**Path:** `mesh_public/index.html` (also `mesh_public/nexus.html`)

Multi-threaded **4D neural ecosystem**:
- Web Worker computes positions + 4×4 neural matrices
- Zero-copy Transferable ArrayBuffers (state + brains)
- Main thread renders ~60fps projection (x,y,z → screen; w → hue)
- Up to 5000 organism slots (default 1000 active)

## Links
- VIVARIUM: `vivarium.html`
- LUMEN: `lumen.html`

## Local preview
```bash
cd mesh_public && python3 -m http.server 8765
```
