# Validate Product KB

Run:

```bash
python scripts/validate.py
python scripts/check_conflicts.py
pytest
```

Validation should check schemas, required files, media references, transcript files, and claim conflicts.

Fix source files first. Rebuild derived artifacts only after source validation passes.
