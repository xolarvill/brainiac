from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from kb import (
    available_variant_options,
    build_customer_support_context,
    inherited_variant_facts,
    load_product,
    load_variant_axes,
    load_variants,
    markdown_bundle,
    product_dir,
    resolve_variant,
    source_evidence,
)

router = APIRouter(prefix="/context")


class ContextRequest(BaseModel):
    product_id: str
    sku_id: str | None = None
    variant_identifier: str | None = None
    variant_options: dict[str, Any] = Field(default_factory=dict)
    page_mode: Literal["family", "variant", "comparison"] = "family"
    customer_question: str | None = None
    language: str = "en"
    channel: str | None = None


class ClaimBoundaries(BaseModel):
    allowed: list[str]
    need_evidence: list[str]
    forbidden: list[str]


class CustomerSupportContext(BaseModel):
    product_id: str
    parent_product_id: str
    sku_id: str | None
    relevant_facts: list[dict[str, Any]]
    variant_facts: dict[str, Any]
    variant_options: dict[str, Any]
    inherited_facts: dict[str, Any]
    resolution: dict[str, Any]
    care_instructions: list[str]
    claim_boundaries: ClaimBoundaries
    suggested_answer_style: str
    must_not_say: list[str]
    golden_qa: list[dict[str, Any]]
    retrieved_evidence: list[dict[str, str]]
    evidence: list[dict[str, Any]]
    source_files: list[str]


class ListingContext(BaseModel):
    product_id: str
    parent_product_id: str
    page_mode: Literal["family", "variant", "comparison"]
    parent_product: dict[str, Any]
    variant_facts: list[dict[str, Any]]
    variant_axes: list[dict[str, Any]]
    selected_variant: dict[str, Any] | None
    resolution: dict[str, Any]
    inherited_facts: dict[str, Any]
    available_options: dict[str, list[Any]]
    positioning: dict[str, Any]
    allowed_claims: list[str]
    forbidden_claims: list[str]
    evidence: list[dict[str, Any]]
    source_files: list[str]


class AdCopyContext(BaseModel):
    product_id: str
    allowed_claims: list[str]
    need_evidence: list[str]
    forbidden_claims: list[str]
    tone: str
    evidence: list[dict[str, Any]]


class SeoContext(BaseModel):
    product_id: str
    topics: list[str]
    faq_source: str
    long_tail_question_ideas: list[str]
    forbidden_claims: list[str]
    evidence: list[dict[str, Any]]


def ensure_product(product_id: str) -> None:
    if not product_dir(product_id).exists():
        raise HTTPException(status_code=404, detail="Product not found")


def resolve_request_variant(request: ContextRequest) -> dict[str, Any]:
    identifier = request.variant_identifier or request.sku_id
    resolution = resolve_variant(request.product_id, identifier, request.variant_options)
    if resolution["status"] == "not_found" and (identifier or request.variant_options):
        raise HTTPException(status_code=404, detail="Variant not found")
    if resolution["status"] == "ambiguous":
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Variant selection is ambiguous",
                "matches": [variant.get("sku_id") for variant in resolution["matches"]],
            },
        )
    return resolution


@router.post("/customer-support", response_model=CustomerSupportContext)
def customer_support_context(request: ContextRequest) -> CustomerSupportContext:
    ensure_product(request.product_id)
    resolution = resolve_request_variant(request)
    selected = resolution["selected_variant"] or {}
    selected_sku = selected.get("sku_id") or request.sku_id
    context = build_customer_support_context(
        request.product_id,
        selected_sku,
        customer_question=request.customer_question,
    )
    context["resolution"] = resolution
    return CustomerSupportContext.model_validate(context)


@router.post("/listing", response_model=ListingContext)
def listing_context(request: ContextRequest) -> ListingContext:
    ensure_product(request.product_id)
    product = load_product(request.product_id)
    resolution = resolve_request_variant(request)
    if request.page_mode == "variant" and resolution["status"] != "matched":
        raise HTTPException(status_code=409, detail="A variant page requires one resolved variant")
    selected = resolution["selected_variant"]
    axes = load_variant_axes(request.product_id)
    return ListingContext(
        product_id=request.product_id,
        parent_product_id=request.product_id,
        page_mode=request.page_mode,
        parent_product=product,
        variant_facts=load_variants(request.product_id),
        variant_axes=axes,
        selected_variant=selected,
        resolution=resolution,
        inherited_facts=inherited_variant_facts(product, selected, axes),
        available_options=available_variant_options(request.product_id),
        positioning=product.get("brand_positioning", {}),
        allowed_claims=product.get("claims_allowed", []),
        forbidden_claims=product.get("claims_forbidden", []),
        evidence=source_evidence(request.product_id, selected),
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
        tone=product.get("copy_guidance", {}).get("tone", "clear, source-backed, cautious"),
        evidence=source_evidence(request.product_id),
    )


@router.post("/seo", response_model=SeoContext)
def seo_context(request: ContextRequest) -> SeoContext:
    ensure_product(request.product_id)
    product = load_product(request.product_id)
    modules = markdown_bundle(request.product_id)
    variant_axes = load_variant_axes(request.product_id)
    product_name = product.get("product_name", "this product")
    question_ideas = [
        f"Which {axis.get('label', axis.get('key'))} should I choose for {product_name}?"
        for axis in variant_axes
        if axis.get("key")
    ] or [f"What should I know before choosing {product_name}?"]
    return SeoContext(
        product_id=request.product_id,
        topics=product.get("common_facts", {}).get("use_cases", []),
        faq_source=modules["faq.md"],
        long_tail_question_ideas=question_ideas,
        forbidden_claims=product.get("claims_forbidden", []),
        evidence=source_evidence(request.product_id),
    )
