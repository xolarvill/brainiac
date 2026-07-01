# Validate Product KB

Run:

```bash
uv run python scripts/validate.py
uv run python scripts/check_conflicts.py
uv run pytest
```

Validation should check schemas, required files, media references, transcript files, and claim conflicts.

Fix source files first. Rebuild derived artifacts only after source validation passes.
