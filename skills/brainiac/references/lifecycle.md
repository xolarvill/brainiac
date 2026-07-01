# Product KB Lifecycle

Use this reference for cross-cutting product knowledge tasks that do not fit only initialization, accumulation, or maintenance.

## Operating Rules

- Product knowledge must be written into the target repository as version-controlled files.
- Initialize from `template/` on first use.
- Enter maintenance mode when the target repo already exists.
- Treat YAML, JSON, Markdown, media manifests, and source files as the source of truth.
- Treat SQLite indexes and exports as derived artifacts.
- Update structured files before derived Markdown when facts change.
- Keep source notes, official knowledge, media assets, indexes, and exports separated.
- Run validation after changes.
- Never invent unsupported product claims.
- Never make medical, veterinary, legal, or compliance claims unless backed by source files.
- Record missing information in `source-notes.md` instead of fabricating.
- Keep raw source material on disk under `sources/<product-slug>/`; do not use chat history as the source store.

## Product Model

- `product.yaml`: SPU-level facts shared by all SKUs.
- `variants.yaml`: SKU facts such as size, color, dimensions, package details, and media refs.
- Markdown modules: FAQ, objections, care, compliance, comparison, and source context.
- `media/media.yaml`: media metadata; product text should reference asset IDs, not embed files.
- `golden-qa.yaml`: evaluation questions and expected answer policies.

## Raw Source Intake

Use this product-scoped layout:

```text
sources/<product-slug>/
  supplier-docs/
  competitor-pages/
  customer-reviews/
  customer-support/
  interview-notes/
  media-inbox/
```

The user should provide paths to source folders or files. Codex should read from disk, extract facts, and write durable knowledge under `products/<product_id>/`.

## Command Groups

Initialize:

```bash
UV_CACHE_DIR=.uv-cache uv sync --extra dev
UV_CACHE_DIR=.uv-cache uv run python scripts/validate.py
UV_CACHE_DIR=.uv-cache uv run pytest
```

Validate:

```bash
UV_CACHE_DIR=.uv-cache uv run python scripts/validate.py
UV_CACHE_DIR=.uv-cache uv run python scripts/check_conflicts.py
UV_CACHE_DIR=.uv-cache uv run pytest
```

Export:

```bash
UV_CACHE_DIR=.uv-cache uv run python scripts/export_support_context.py
UV_CACHE_DIR=.uv-cache uv run python scripts/export_shopify.py
```

Rebuild search index:

```bash
UV_CACHE_DIR=.uv-cache uv run python scripts/build_index.py
```
