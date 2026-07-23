from __future__ import annotations

from typing import Any

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


class ClaimBoundaries(BaseModel):
    allowed: list[str]
    need_evidence: list[str]
    forbidden: list[str]


class CustomerSupportContext(BaseModel):
    product_id: str
    sku_id: str | None
    relevant_facts: list[dict[str, Any]]
    variant_facts: dict[str, Any]
    care_instructions: list[str]
    claim_boundaries: ClaimBoundaries
    suggested_answer_style: str
    must_not_say: list[str]
    golden_qa: list[dict[str, Any]]
    source_files: list[str]


class ListingContext(BaseModel):
    product_id: str
    variant_facts: list[dict[str, Any]]
    positioning: dict[str, Any]
    allowed_claims: list[str]
    forbidden_claims: list[str]
    source_files: list[str]


class AdCopyContext(BaseModel):
    product_id: str
    allowed_claims: list[str]
    need_evidence: list[str]
    forbidden_claims: list[str]
    tone: str


class SeoContext(BaseModel):
    product_id: str
    topics: list[str]
    faq_source: str
    long_tail_question_ideas: list[str]
    forbidden_claims: list[str]


def ensure_product(product_id: str) -> None:
    if not product_dir(product_id).exists():
        raise HTTPException(status_code=404, detail="Product not found")


@router.post("/customer-support", response_model=CustomerSupportContext)
def customer_support_context(request: ContextRequest) -> CustomerSupportContext:
    ensure_product(request.product_id)
    return CustomerSupportContext.model_validate(build_customer_support_context(request.product_id, request.sku_id))


@router.post("/listing", response_model=ListingContext)
def listing_context(request: ContextRequest) -> ListingContext:
    ensure_product(request.product_id)
    product = load_product(request.product_id)
    return ListingContext(
        product_id=request.product_id,
        variant_facts=load_variants(request.product_id),
        positioning=product.get("brand_positioning", {}),
        allowed_claims=product.get("claims_allowed", []),
        forbidden_claims=product.get("claims_forbidden", []),
        source_files=[f"products/{request.product_id}/product.yaml", f"products/{request.product_id}/variants.yaml"],
    )


@router.post("/ad-copy", response_model=AdCopyContext)
def ad_copy_context(request: ContextRequest) -> AdCopyContext:
    ensure_product(request.product_id)
    product = load_product(request.product_id)
    return AdCopyContext(
        product_id=request.product_id,
        allowed_claims=product.get("claims_allowed", []),
        need_evidence=product.get("claims_need_evidence", []),
        forbidden_claims=product.get("claims_forbidden", []),
        tone="benefit-led, cautious, no medical promises",
    )


@router.post("/seo", response_model=SeoContext)
def seo_context(request: ContextRequest) -> SeoContext:
    ensure_product(request.product_id)
    product = load_product(request.product_id)
    modules = markdown_bundle(request.product_id)
    return SeoContext(
        product_id=request.product_id,
        topics=product.get("common_facts", {}).get("use_cases", []),
        faq_source=modules["faq.md"],
        long_tail_question_ideas=[
            f"Which {product.get('product_name')} size should I choose?",
            f"How do I clean a {product.get('product_name')}?",
            f"Is a {product.get('product_name')} suitable for senior dogs?",
        ],
        forbidden_claims=product.get("claims_forbidden", []),
    )
