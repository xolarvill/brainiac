# Brainiac

Local-first product knowledge base for SKU-level ecommerce knowledge accumulation and AI-agent consumption.

This repository is a monorepo with two parts:

- `skills/`: Codex-discoverable skills for initialization, accumulation, and maintenance.
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
uv run python scripts/new_product.py orthopedic-dog-bed
uv run python scripts/validate.py
uv run python scripts/check_conflicts.py
uv run python scripts/build_index.py
uv run python scripts/export_support_context.py
uv run uvicorn api.main:app --reload --port 8710
uv run pytest
```

## Agent Use

On first use, copy `template/` into a new product knowledge repository. Future agents should read `AGENT.md`, update structured facts first, keep source notes separate from official knowledge, run validation, and rebuild derived artifacts when needed.

The system starts with customer support QA, but the same files can support listing, SEO, ad copy, content, and media pipeline agents.

## User Workflow After Installing

Brainiac is a workflow plugin, not the place where product knowledge lives. After installing the plugin, create a separate product knowledge repo for your store or product line.

```text
my-store-product-kb/
```

Ask Codex:

```text
$product-kb-init initialize this folder as a Brainiac product knowledge repo
```

Then place raw materials on disk, not in the Codex chat window. The chat should contain the task and paths only.

Recommended raw source layout:

```text
sources/
  orthopedic-dog-bed/
    supplier-docs/
    competitor-pages/
    customer-reviews/
    customer-support/
    interview-notes/
    media-inbox/
```

Drop supplier PDFs, copied product specs, review exports, support transcripts, interview notes, competitor page captures, image files, video files, and transcript drafts into those folders. For large webpages or PDFs, save them as files first. Do not paste long source dumps into chat unless the source is tiny.

Then ask Codex:

```text
$product-kb-accumulate ingest sources/orthopedic-dog-bed into products/orthopedic-dog-bed
```

Codex should read the source files from disk, extract facts, and write the source of truth into:

```text
products/orthopedic-dog-bed/product.yaml
products/orthopedic-dog-bed/variants.yaml
products/orthopedic-dog-bed/*.md
products/orthopedic-dog-bed/golden-qa.yaml
products/orthopedic-dog-bed/media/media.yaml
```

Use chat for judgment and direction:

```text
$product-kb-update update ODB-GREY-L dimensions from sources/orthopedic-dog-bed/supplier-docs/2026-size-sheet.pdf
$product-kb-update add the new washing limitation from sources/orthopedic-dog-bed/customer-support/june-tickets.md
```

Brainiac's job is to grill raw source folders into durable product knowledge files. It should not treat the conversation context as the knowledge store.

## Skill And Plugin Packaging

`skills/` is the only skill directory. The Codex plugin manifest in `.codex-plugin/plugin.json` points there directly. Do not create a separate `skill/` folder; it creates needless ambiguity.

Marketplace install:

```bash
codex plugin marketplace add xolarvill/brainiac --ref main
codex plugin add brainiac@brainiac
```

Current skill split:

- `$brainiac`: broad entrypoint and cross-cutting references.
- `$product-kb-init`: initialize a repo from `template/`, install uv dependencies, validate the example, and start the optional API.
- `$product-kb-accumulate`: turn source material into SPU/SKU YAML, Markdown modules, golden QA, and media manifests.
- `$product-kb-update`: maintain facts, claims, variants, media, exports, indexes, and API behavior without editing derived artifacts as source truth.

For local plugin development, update this repository, reinstall or refresh the plugin in Codex, then start a new thread so Codex reloads the skill metadata.
