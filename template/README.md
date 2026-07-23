# Product Knowledge Repository

This is a local-first product knowledge repository for ecommerce products.

YAML, Markdown, media manifests, and source files are the source of truth. Indexes and exports are derived and reproducible.

## Structure

- `products/<product_id>/product.yaml`: SPU-level product facts.
- `products/<product_id>/variants.yaml`: SKU-level facts.
- `products/<product_id>/*.md`: human-readable knowledge modules.
- `products/<product_id>/media/media.yaml`: media asset manifest.
- `products/<product_id>/raw/`: raw source files for that product.
- `products/<product_id>/sources.yaml`: hashed inventory of imported raw files.
- `schemas/`: JSON schemas used by validation.
- `scripts/`: local maintenance, validation, indexing, and export scripts.
- `api/`: optional FastAPI service.
- `indexes/`: derived search indexes.
- `exports/`: derived contexts for agents and channels.
- `ACCESS.md`: instructions for agents that consume the knowledge base.

## Raw Source Intake

Put raw materials in `products/<product_id>/raw/` and pass Codex the path. Do not paste long supplier docs, reviews, transcripts, or competitor pages into the chat window.

Recommended layout:

```text
products/
  orthopedic-dog-bed/
    raw/
      supplier-docs/
      competitor-pages/
      customer-reviews/
      customer-support/
      interview-notes/
      media-inbox/
```

Examples:

```text
$product-kb-accumulate ingest products/orthopedic-dog-bed/raw into products/orthopedic-dog-bed
$product-kb-update update ODB-GREY-L using products/orthopedic-dog-bed/raw/supplier-docs/2026-size-sheet.pdf
```

After Codex reads the source files, durable facts should be written into `products/<product_id>/`. Keep unresolved or weak evidence in `source-notes.md`.

## Setup

```bash
uv sync --extra dev
```

## Common Commands

```bash
uv run python scripts/new_product.py orthopedic-dog-bed
uv run python scripts/ingest_sources.py orthopedic-dog-bed /path/to/source-folder
uv run python scripts/validate.py
uv run python scripts/check_conflicts.py
uv run python scripts/build_index.py
uv run python scripts/export_support_context.py
uv run uvicorn api.main:app --reload --port 8710
uv run pytest
```

The scripts also work as plain `python scripts/...` commands inside an activated uv-managed environment.

`ingest_sources.py` optionally copies a file or folder into `raw/imported/`, writes `sources.yaml`, and rebuilds `indexes/product_kb.sqlite`. It never edits curated product facts. Text, table, structured-data, and HTML files are searchable; binary files are inventoried but not extracted.

## Agent Guidance

Agents should read `AGENT.md` before editing. Update structured facts before Markdown, never invent product claims, and record missing information in `source-notes.md`.

## Optional Local API

Start the API:

```bash
uv run uvicorn api.main:app --reload --port 8710
```

Example request:

```bash
curl -X POST http://127.0.0.1:8710/context/customer-support \
  -H 'Content-Type: application/json' \
  -d '{"product_id":"example-orthopedic-dog-bed","sku_id":"ODB-GREY-L","customer_question":"Can this bed help my old dog with arthritis?","language":"en","channel":"shopify_chat"}'
```
