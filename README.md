# mvw-parser-higgsfield-content-factory

Parser for higgsfield.ai/content-factory (preset videos, stats; SSR batch only, see TODO).

```bash
./run.sh --limit 5   # try
./run.sh              # full, idempotent (skips files already downloaded)
```

Stdlib only, Python 3.9+. For the scroll, set `MVW_PYTHON` to a Python with `camoufox` installed (otherwise static HTML fallback). Layout and schema live in `../mvw-core`.
