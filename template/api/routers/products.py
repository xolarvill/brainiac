from __future__ import annotations

from fastapi import APIRouter, HTTPException

from kb import load_product, product_dir, product_dirs

router = APIRouter()


@router.get("/products")
def list_products() -> list[str]:
    return [folder.name for folder in product_dirs()]


@router.get("/products/{product_id}")
def get_product(product_id: str) -> dict:
    if not product_dir(product_id).exists():
        raise HTTPException(status_code=404, detail="Product not found")
    return load_product(product_id)
