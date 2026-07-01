# Product Knowledge Base Skill

Use this skill when initializing or maintaining a local-first ecommerce product knowledge repository.

This skill defines workflows only. It does not store product knowledge itself. Product knowledge must be written into the target repository as version-controlled source files.

## Operating Rules

- On first use, initialize from `template/`.
- If the target project already exists, enter maintenance mode.
- Treat YAML, JSON, Markdown, and media manifests as the source of truth.
- Treat SQLite indexes and exported contexts as derived artifacts.
- Always update structured files before derived Markdown when facts change.
- Keep source notes, official knowledge, media assets, indexes, and exports separated.
- Always run validation after changes.
- Never invent unsupported product claims.
- Never make medical, veterinary, legal, or compliance claims unless backed by source files.
- When information is missing, create a clear missing-info list instead of fabricating.

## Product Model

- `product.yaml` stores SPU-level facts shared by all SKUs.
- `variants.yaml` stores SKU-specific facts such as size, color, dimensions, package details, and media references.
- Markdown modules store human-readable support, care, compliance, comparison, and source context.
- `media/media.yaml` describes media assets; product text should reference asset IDs instead of embedding media files.

## Required Workflow

1. Read `AGENT.md` in the target repo.
2. Identify whether the task is initialization, ingestion, update, validation, or export.
3. Update source files only.
4. Run validation and conflict checks.
5. Rebuild indexes or exports only when requested or required by the task.

See `workflows/` for task-specific steps.
