from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from kb import build_customer_support_context, load_product, load_variants, markdown_bundle, product_dir

router = APIRouter(prefix="/context")


class ContextRequest(BaseModel):
    product_id: str
    sku_id: str | None = None
    customer_question: str | None = None
    language: str = "en"
    channel: str | None = None


def ensure_product(product_id: str) -> None:
    if not product_dir(product_id).exists():
        raise HTTPException(status_code=404, detail="Product not found")


@router.post("/customer-support")
def customer_support_context(request: ContextRequest) -> dict:
    ensure_product(request.product_id)
    return build_customer_support_context(request.product_id, request.sku_id)


@router.post("/listing")
def listing_context(request: ContextRequest) -> dict:
    ensure_product(request.product_id)
    product = load_product(request.product_id)
    return {
        "product_id": request.product_id,
        "variant_facts": load_variants(request.product_id),
        "positioning": product.get("brand_positioning", {}),
        "allowed_claims": product.get("claims_allowed", []),
        "forbidden_claims": product.get("claims_forbidden", []),
        "source_files": [f"products/{request.product_id}/product.yaml", f"products/{request.product_id}/variants.yaml"],
    }


@router.post("/ad-copy")
def ad_copy_context(request: ContextRequest) -> dict:
    ensure_product(request.product_id)
    product = load_product(request.product_id)
    return {
        "product_id": request.product_id,
        "allowed_claims": product.get("claims_allowed", []),
        "need_evidence": product.get("claims_need_evidence", []),
        "forbidden_claims": product.get("claims_forbidden", []),
        "tone": "benefit-led, cautious, no medical promises",
    }


@router.post("/seo")
def seo_context(request: ContextRequest) -> dict:
    ensure_product(request.product_id)
    product = load_product(request.product_id)
    modules = markdown_bundle(request.product_id)
    return {
        "product_id": request.product_id,
        "topics": product.get("common_facts", {}).get("use_cases", []),
        "faq_source": modules["faq.md"],
        "long_tail_question_ideas": [
            f"Which {product.get('product_name')} size should I choose?",
            f"How do I clean a {product.get('product_name')}?",
            f"Is a {product.get('product_name')} suitable for senior dogs?",
        ],
        "forbidden_claims": product.get("claims_forbidden", []),
    }
