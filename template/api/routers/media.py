from __future__ import annotations

from fastapi import APIRouter, HTTPException

from kb import load_media, product_dir

router = APIRouter()


@router.get("/products/{product_id}/media")
def get_media(product_id: str) -> dict:
    if not product_dir(product_id).exists():
        raise HTTPException(status_code=404, detail="Product not found")
    return load_media(product_id)
