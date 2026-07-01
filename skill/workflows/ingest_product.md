# Ingest Product

1. Create a product folder with `python scripts/new_product.py <product-slug>`.
2. Fill `product.yaml` with SPU-level facts.
3. Fill `variants.yaml` with SKU-level facts.
4. Add Markdown modules for FAQ, objections, care, compliance, comparison, and source notes.
5. Add media metadata to `media/media.yaml`; store files under `media/images`, `media/videos`, and `media/transcripts`.
6. Add `golden-qa.yaml` for support-agent evaluation.
7. Run validation and conflict checks.

If facts are missing, record them in `source-notes.md` under unresolved questions.
