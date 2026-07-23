# Agent Access Manual

This repository is the source of truth for product knowledge. Consuming agents can read it directly or through the optional local API.

## Rules For All Agents

- Treat YAML, Markdown, `golden-qa.yaml`, and `media/media.yaml` as source truth.
- Treat `indexes/` and `exports/` as derived artifacts.
- Treat `products/<product_id>/raw/` as evidence only, not official product knowledge.
- Treat `products/<product_id>/sources.yaml` as the machine-readable inventory of raw evidence.
- Do not make claims listed in `claims_forbidden`.
- Do not present `claims_need_evidence` as proven unless a source file supports it.
- Prefer media transcripts and metadata over raw video files.

## Direct File Access

Read these files for a product:

```text
products/<product_id>/product.yaml
products/<product_id>/variants.yaml
products/<product_id>/faq.md
products/<product_id>/objections.md
products/<product_id>/care-guide.md
products/<product_id>/compliance.md
products/<product_id>/comparison.md
products/<product_id>/golden-qa.yaml
products/<product_id>/media/media.yaml
products/<product_id>/sources.yaml
```

Use `source-notes.md` for evidence gaps, unresolved questions, and human judgment.

## API Access

Start the local API:

```bash
uv run uvicorn api.main:app --reload --port 8710
```

Useful endpoints:

```text
GET  /health
GET  /products
GET  /products/{product_id}
GET  /products/{product_id}/variants
GET  /products/{product_id}/media
GET  /products/{product_id}/sources
POST /context/customer-support
POST /context/listing
POST /context/ad-copy
POST /context/seo
GET  /search?q=...&product_id=...
```

Context request shape:

```json
{
  "product_id": "example-orthopedic-dog-bed",
  "sku_id": "ODB-GREY-L",
  "customer_question": "Can this bed help my old dog with arthritis?",
  "language": "en",
  "channel": "shopify_chat"
}
```

## Which Access Mode To Use

- Use direct files when an agent can work inside the repo and needs full traceability.
- Use FastAPI when another local tool or agent needs a stable interface.
- Use exports when the consumer only needs a reproducible context bundle.
- Use `/search` when the consumer needs source-backed snippets; preserve each result's `source_id` and `path` in the generated answer.
