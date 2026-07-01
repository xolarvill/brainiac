---
name: product-kb-system
description: Initialize and maintain local-first ecommerce product knowledge repositories for SKU-level AI-agent consumption. Use for product knowledge repo setup, ingestion, validation, export, and maintenance workflows.
---

# Product KB System

This is the broad Codex plugin entrypoint. Prefer the narrower skills:

- Use `$product-kb-init` to initialize a product knowledge repository from `template/`.
- Use `$product-kb-accumulate` to ingest source material into SPU/SKU knowledge files.
- Use `$product-kb-update` to maintain facts, claims, media, exports, indexes, and API behavior.

For cross-cutting tasks, load only the needed reference:

- `references/lifecycle.md` for source-of-truth rules, product model, and command groups.
- `references/prompt-patterns.md` for reusable agent prompts.

Do not duplicate product knowledge inside plugin metadata, prompts, chat history, or hidden memory.
