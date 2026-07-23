# Brainiac

Local-first product knowledge base for SKU-level ecommerce knowledge accumulation and AI-agent consumption.

This repository is a monorepo with two parts:

- `skills/`: Codex-discoverable skills for initialization, accumulation, and maintenance.
- `template/`: a copyable product knowledge repository template with source files, validation scripts, exports, and an optional local FastAPI service.

Product knowledge is treated as a version-controlled business asset. YAML, JSON, Markdown, and media manifests are the source of truth. SQLite indexes and exported contexts are derived artifacts that can be rebuilt.

## Architecture

- Product facts: `products/<product_id>/product.yaml`
- Variant axes and SKU/model facts: `products/<product_id>/variants.yaml`
- Raw source inventory: `products/<product_id>/sources.yaml`
- Human-readable modules: Markdown files beside each product.
- Media metadata: `products/<product_id>/media/media.yaml`
- Media files: stored under product `media/` folders.
- Derived indexes: `indexes/`
- Derived exports: `exports/`
- Optional local API: `api/`

## Quick Start

```bash
cd template
uv run python scripts/new_product.py <product-slug>
uv run python scripts/ingest_sources.py <product-id> /path/to/source-folder
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

Recommended product folder layout:

```text
products/
  <product-id>/
    raw/
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
$product-kb-accumulate ingest products/<product-id>/raw into products/<product-id>
```

For a repeatable local import, use the repository command. It copies an optional file/folder into `raw/imported/`, records every raw file in `sources.yaml`, and rebuilds the SQLite index:

```bash
cd template
uv run python scripts/ingest_sources.py <product-id> /path/to/source-folder
```

Markdown, text, CSV, JSON, YAML, and HTML sources are searchable immediately. Images, video, and PDFs are retained and tracked in `sources.yaml` until a media/OCR/PDF extractor is added.

Codex should read the source files from disk, extract facts, and write the source of truth into:

```text
products/<product-id>/product.yaml
products/<product-id>/variants.yaml
products/<product-id>/*.md
products/<product-id>/golden-qa.yaml
products/<product-id>/media/media.yaml
```

Use chat for judgment and direction:

```text
$product-kb-update update MODEL-001 options from products/<product-id>/raw/supplier-docs/2026-spec-sheet.pdf
$product-kb-update add a source-backed product fact from products/<product-id>/raw/customer-support/june-tickets.md
```

Brainiac's job is to grill raw source folders into durable product knowledge files. It should not treat the conversation context as the knowledge store.

## Agent Access

Potential consuming agents should start with `template/ACCESS.md` after a repo is initialized.

- Direct file agents read `products/<product_id>/product.yaml`, `variants.yaml`, Markdown modules, `golden-qa.yaml`, and `media/media.yaml`.
- API agents call `/products`, `/products/{product_id}`, `/products/{product_id}/variants`, `/products/{product_id}/media`, `/context/*`, and `/search`.
- Downstream agents can call `/products/{product_id}/sources` for source metadata and `/search?q=...&product_id=...` for evidence snippets with `source_id` and `path`.
- For multi-variant pages, resolve a model/SKU or option combination first; an ambiguous result must remain a selection request.
- Neither type should treat `products/<product_id>/raw/` as official product knowledge. Raw files are evidence for maintenance and accumulation.

## Skill And Plugin Packaging

`skills/` is the only skill directory. The Codex plugin manifest in `.codex-plugin/plugin.json` points there directly. Do not create a separate `skill/` folder; it creates needless ambiguity.

Marketplace install:

```bash
codex plugin marketplace add xolarvill/brainiac --ref master
codex plugin add brainiac@brainiac
```

Current skill split:

- `$brainiac`: broad entrypoint and cross-cutting references.
- `$product-kb-init`: initialize a repo from `template/`, install uv dependencies, validate the example, and start the optional API.
- `$product-kb-accumulate`: turn source material into SPU/SKU YAML, Markdown modules, golden QA, and media manifests.
- `$product-kb-update`: maintain facts, claims, variants, media, exports, indexes, and API behavior without editing derived artifacts as source truth.

For local plugin development, update this repository, reinstall or refresh the plugin in Codex, then start a new thread so Codex reloads the skill metadata.
