from __future__ import annotations

from fastapi import APIRouter, Query

from kb import index_search

router = APIRouter()


@router.get("/search")
def search(q: str = Query(..., min_length=1)) -> list[dict[str, str]]:
    return index_search(q)
