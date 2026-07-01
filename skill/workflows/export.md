# Export Product Context

Run:

```bash
uv run python scripts/export_support_context.py
uv run python scripts/export_shopify.py
```

Exports are derived artifacts. If an export looks wrong, fix the source YAML or Markdown first, then regenerate.

Exports must respect `claims_forbidden` and claim evidence boundaries.
