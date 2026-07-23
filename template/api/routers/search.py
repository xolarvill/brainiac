from __future__ import annotations

from fastapi import APIRouter, Query

from kb import index_search

router = APIRouter()


@router.get("/search")
def search(
    q: str = Query(..., min_length=1),
    product_id: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[dict[str, str]]:
    return index_search(q, product_id=product_id, limit=limit)
