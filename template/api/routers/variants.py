from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from kb import load_variants, product_dir, resolve_variant

router = APIRouter()


class VariantResolveRequest(BaseModel):
    identifier: str | None = None
    options: dict[str, Any] = Field(default_factory=dict)


@router.get("/products/{product_id}/variants")
def get_variants(product_id: str) -> list[dict]:
    if not product_dir(product_id).exists():
        raise HTTPException(status_code=404, detail="Product not found")
    return load_variants(product_id)


@router.post("/products/{product_id}/variants/resolve")
def resolve_product_variant(product_id: str, request: VariantResolveRequest) -> dict[str, Any]:
    if not product_dir(product_id).exists():
        raise HTTPException(status_code=404, detail="Product not found")
    return resolve_variant(product_id, request.identifier, request.options)
