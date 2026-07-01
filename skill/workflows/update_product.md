# Update Product

1. Identify whether the change is SPU-level or SKU-level.
2. Update `product.yaml` for shared facts.
3. Update `variants.yaml` for SKU-specific facts.
4. Update Markdown modules only after structured facts are corrected.
5. Update `media/media.yaml` when adding, replacing, or retiring assets.
6. Add source notes for why the change is trusted.
7. Run:

```bash
python scripts/validate.py
python scripts/check_conflicts.py
```

Never silently weaken claim boundaries to make copy easier.
