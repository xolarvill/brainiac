# Product KB System

Local-first product knowledge base system for SKU-level ecommerce knowledge accumulation and AI-agent consumption.

This repository is a monorepo with two parts:

- `skill/`: instructions for Codex-like agents that initialize and maintain product knowledge repositories.
- `template/`: a copyable product knowledge repository template with source files, validation scripts, exports, and an optional local FastAPI service.

Product knowledge is treated as a version-controlled business asset. YAML, JSON, Markdown, and media manifests are the source of truth. SQLite indexes and exported contexts are derived artifacts that can be rebuilt.

## Architecture

- Product facts: `products/<product_id>/product.yaml`
- Variant/SKU facts: `products/<product_id>/variants.yaml`
- Human-readable modules: Markdown files beside each product.
- Media metadata: `products/<product_id>/media/media.yaml`
- Media files: stored under product `media/` folders.
- Derived indexes: `indexes/`
- Derived exports: `exports/`
- Optional local API: `api/`

## Quick Start

```bash
cd template
python scripts/new_product.py orthopedic-dog-bed
python scripts/validate.py
python scripts/check_conflicts.py
python scripts/build_index.py
python scripts/export_support_context.py
uvicorn api.main:app --reload --port 8710
pytest
```

## Agent Use

On first use, copy `template/` into a new product knowledge repository. Future agents should read `AGENT.md`, update structured facts first, keep source notes separate from official knowledge, run validation, and rebuild derived artifacts when needed.

The system starts with customer support QA, but the same files can support listing, SEO, ad copy, content, and media pipeline agents.
