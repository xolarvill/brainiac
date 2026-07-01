# Initialize Product KB

1. Copy `template/` into the target repository.
2. Rename the copied folder if needed.
3. Read `AGENT.md`.
4. Run:

```bash
python scripts/validate.py
pytest
```

5. Commit the initialized source files.

Do not move example product knowledge into prompts or chat memory. Keep it as files.
