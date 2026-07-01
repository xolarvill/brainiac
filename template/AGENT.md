# Agent Operating Manual

This repository stores product knowledge as version-controlled source files.

## Directory Rules

- `products/` contains one folder per product.
- `products/<product_id>/raw/` stores raw or lightly processed source material for that product.
- `indexes/` stores derived SQLite/search indexes.
- `exports/` stores derived agent contexts and channel snippets.
- `api/` exposes an optional local service over the same source files.
- `ACCESS.md` explains how consuming agents should read this repository.

## Product Modeling

- SPU-level shared facts live in `product.yaml`.
- SKU/variant-specific facts live in `variants.yaml`.
- Markdown modules explain facts for humans and agents.
- `golden-qa.yaml` contains evaluation questions and expected answer policies.

## Source Intake

Prefer `products/<product_id>/raw/` for raw materials tied to one product. Use subfolders such as `supplier-docs`, `competitor-pages`, `customer-reviews`, `customer-support`, `interview-notes`, and `media-inbox`.

Read source files from disk. Do not ask users to paste large raw documents into chat. If a source is missing, write the gap in `source-notes.md`.

## Media Handling

- Do not embed media files into product text.
- Store media files under `media/images`, `media/videos`, or `media/transcripts`.
- Describe assets in `media/media.yaml`.
- Video agents should consume transcript and metadata before raw video.
- Future Git LFS, S3, R2, or MinIO support can be added behind the manifest without changing product facts.

## Claim Boundaries

- Allowed claims are in `product.yaml`.
- Evidence-required claims must not be presented as proven unless source files support them.
- Forbidden claims must not appear in FAQ, objections, care guides, comparison copy, exports, or generated answers.
- Do not provide medical, veterinary, legal, or compliance advice unless backed by source files.

## Update Workflow

1. Update source YAML first.
2. Update Markdown modules second.
3. Update media manifest if assets change.
4. Add source notes and unresolved questions.
5. Run validation and conflict checks.
6. Rebuild indexes or exports only after source files pass.

## Commands

```bash
uv run python scripts/new_product.py orthopedic-dog-bed
uv run python scripts/new_variant.py example-orthopedic-dog-bed ODB-GREY-S --size S --color Grey --length-cm 60 --width-cm 45 --height-cm 14 --min-weight-kg 3 --max-weight-kg 8
uv run python scripts/validate.py
uv run python scripts/check_conflicts.py
uv run python scripts/build_index.py
uv run python scripts/export_support_context.py
uv run python scripts/export_shopify.py
uv run uvicorn api.main:app --reload --port 8710
uv run pytest
```

## Safe Changes

- New product: use `scripts/new_product.py`.
- New variant: use `scripts/new_variant.py`.
- Dimensions: update only `variants.yaml`, then search Markdown for stale values.
- Claims: update `product.yaml`, `compliance.md`, and source notes together.
- Washing instructions: update `product.yaml`, `care-guide.md`, FAQ, and support exports.
- Media assets: add files under `media/`, update `media/media.yaml`, then validate references.
