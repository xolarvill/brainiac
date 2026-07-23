# Prompt Patterns

Use these patterns when a user asks for a reusable instruction or agent handoff.

## New Product

Create a new product knowledge folder for `<product-slug>`.

Use source documents from `products/<product_id>/raw/`, fill structured product and variant facts first, then write Markdown modules. Do not invent unsupported claims. Add unresolved questions to `source-notes.md`. Run validation before finishing.

## Update Variant

Update SKU `<sku_id>` for product `<product_id>`.

Change only SKU-level options, identifiers, attributes, or media refs in `variants.yaml` unless the fact applies to every variant. Resolve the resulting variant combination and rerun validation.

## Customer Support Context

Generate customer-support context for product `<product_id>` and optional SKU `<sku_id>`.

Use only repository source files. Include claim boundaries, product-specific instructions, resolved variant facts, option values, and source file references. If the answer requires an unsupported claim, say what is missing instead.
