---
name: product-kb-init
description: Initialize a local-first ecommerce product knowledge repository from this system's template. Use when Codex needs to create or bootstrap a product knowledge repo, copy the template, verify the source-of-truth layout, install uv dependencies, validate the example product, or expose the optional local FastAPI interface.
---

# Product KB Init

Initialize a repository where product knowledge lives in files, not chat history.

## Workflow

1. Locate this system repo and its `template/` directory.
2. Copy `template/` into the target product knowledge repository.
3. Read the target repo's `AGENT.md` before editing product files.
4. Run setup and checks from the target repo:

```bash
UV_CACHE_DIR=.uv-cache uv sync --extra dev
UV_CACHE_DIR=.uv-cache uv run python scripts/validate.py
UV_CACHE_DIR=.uv-cache uv run pytest
```

5. If the local service is needed, start:

```bash
UV_CACHE_DIR=.uv-cache uv run uvicorn api.main:app --reload --port 8710
```

## Rules

- Keep YAML, Markdown, media manifests, and source files as the source of truth.
- Treat `indexes/` and `exports/` as rebuildable derived artifacts.
- Do not move product facts into prompts, hidden memory, or plugin metadata.
- Leave example product data in place until the initialized repo has its own first real product.

## Completion Check

The init is complete only when `scripts/validate.py` and `pytest` pass in the target repo.

## User-Facing Completion

Keep the final response focused on what the user can act on:

- Say the repository is initialized and whether validation/tests passed.
- Point the user to place raw product material under `products/<product_id>/raw/`.
- Suggest `$product-kb-accumulate` as the next workflow when source files are ready.

Do not surface template maintenance details such as retaining or deleting the example product unless the user asks. The example data is an internal bootstrap fixture, not a next-step instruction.
