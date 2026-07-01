---
name: product-kb-accumulate
description: Accumulate ecommerce product knowledge from supplier docs, reviews, interviews, media, or other source material into SPU-level product.yaml, SKU-level variants.yaml, Markdown knowledge modules, golden QA, and media manifests. Use when Codex needs to ingest a new product, add source-backed facts, or turn messy product evidence into structured local product knowledge.
---

# Product KB Accumulate

Turn source folders into source-backed product knowledge files. Do not ask the user to paste long raw materials into chat.

## Workflow

1. Read `AGENT.md` in the product knowledge repo.
2. Locate raw materials under `sources/<product-slug>/`. If the user pasted a large dump into chat, ask them to save it under `sources/<product-slug>/` and provide the path.
3. Create a product folder when needed:

```bash
UV_CACHE_DIR=.uv-cache uv run python scripts/new_product.py <product-slug>
```

4. Write structured facts first:
   - SPU/common facts in `products/<product_id>/product.yaml`
   - SKU/variant facts in `products/<product_id>/variants.yaml`
   - media metadata in `products/<product_id>/media/media.yaml`
5. Then write human-readable modules:
   - `faq.md`
   - `objections.md`
   - `care-guide.md`
   - `compliance.md`
   - `comparison.md`
   - `source-notes.md`
   - `golden-qa.yaml`
6. Record uncertainty in `source-notes.md`; do not fabricate missing facts.
7. Validate:

```bash
UV_CACHE_DIR=.uv-cache uv run python scripts/validate.py
UV_CACHE_DIR=.uv-cache uv run python scripts/check_conflicts.py
```

## Fact Placement

- Product-wide facts go in `product.yaml`.
- SKU-specific dimensions, colors, weight ranges, package facts, and media refs go in `variants.yaml`.
- Claims and boundaries go in `product.yaml` and `compliance.md`.
- Raw source files go in `sources/<product-slug>/`; unresolved evidence and human judgment go in `source-notes.md`.
- Media files stay under `media/`; agents consume asset IDs and transcripts.

## Claim Rules

- Never invent claims.
- Never turn `claims_need_evidence` into public copy unless the source file supports it.
- Never include `claims_forbidden` in support, listing, ad, SEO, or media outputs except as explicit prohibitions.
