---
name: product-kb-update
description: Maintain an existing ecommerce product knowledge repository by updating facts, variants, dimensions, claims, care instructions, media assets, golden QA, exports, indexes, and local API behavior. Use when Codex needs to safely change product knowledge, preserve source-of-truth files, detect conflicts, validate the repo, or regenerate derived artifacts.
---

# Product KB Update

Update product knowledge without weakening source truth or claim boundaries.

## Workflow

1. Read `AGENT.md` and identify the affected product folder.
2. If raw material was added or replaced, run `scripts/ingest_sources.py` first so `sources.yaml` and the index match disk.
3. Decide the fact level:
   - SPU/common fact: edit `product.yaml`
   - SKU fact: edit `variants.yaml`
   - media fact: edit `media/media.yaml` and transcript files
   - support/copy explanation: edit Markdown modules after structured facts
4. Search related files before changing a fact so stale dimensions or claims do not survive.
5. Update `source-notes.md` with the reason, source, or unresolved gap.
6. Run:

```bash
UV_CACHE_DIR=.uv-cache uv run python scripts/validate.py
UV_CACHE_DIR=.uv-cache uv run python scripts/check_conflicts.py
UV_CACHE_DIR=.uv-cache uv run pytest
```

7. Rebuild derived artifacts only after validation passes:

```bash
UV_CACHE_DIR=.uv-cache uv run python scripts/build_index.py
UV_CACHE_DIR=.uv-cache uv run python scripts/export_support_context.py
UV_CACHE_DIR=.uv-cache uv run python scripts/export_shopify.py
```

## Safe Update Patterns

- Variant options and attributes: update `variants.yaml`, then search Markdown and exports for stale values.
- Claims: update `claims_allowed`, `claims_need_evidence`, `claims_forbidden`, `compliance.md`, and `source-notes.md` together.
- Product-specific care: update `product.yaml`, the relevant Markdown module, and support context exports.
- Media: add or change files under `media/`, update `media.yaml`, and verify all `media_refs`.
- Variant add: prefer `scripts/new_variant.py` unless the SKU shape requires manual fields.

## Do Not

- Do not edit indexes or exports as the source of truth.
- Do not relax forbidden claims to make generated copy nicer.
- Do not leave validation red after a knowledge update.
