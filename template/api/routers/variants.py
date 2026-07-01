from __future__ import annotations

from fastapi import APIRouter, HTTPException

from kb import load_variants, product_dir

router = APIRouter()


@router.get("/products/{product_id}/variants")
def get_variants(product_id: str) -> list[dict]:
    if not product_dir(product_id).exists():
        raise HTTPException(status_code=404, detail="Product not found")
    return load_variants(product_id)
