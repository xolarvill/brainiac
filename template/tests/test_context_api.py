from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_customer_support_context_returns_claim_boundaries() -> None:
    response = client.post(
        "/context/customer-support",
        json={
            "product_id": "example-orthopedic-dog-bed",
            "sku_id": "ODB-GREY-L",
            "customer_question": "Can this bed help my old dog with arthritis?",
            "language": "en",
            "channel": "shopify_chat",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["variant_facts"]["sku_id"] == "ODB-GREY-L"
    assert "cures arthritis" in data["claim_boundaries"]["forbidden"]
    assert data["suggested_answer_style"] == "helpful, cautious, non-medical"
    assert data["retrieved_evidence"]


def test_listing_context_returns_variants_and_sources() -> None:
    response = client.post("/context/listing", json={"product_id": "example-orthopedic-dog-bed"})

    assert response.status_code == 200
    data = response.json()
    assert data["variant_facts"][0]["sku_id"] == "ODB-GREY-M"
    assert data["source_files"] == [
        "products/example-orthopedic-dog-bed/product.yaml",
        "products/example-orthopedic-dog-bed/variants.yaml",
    ]


def test_listing_context_resolves_variant_options() -> None:
    response = client.post(
        "/context/listing",
        json={"product_id": "example-orthopedic-dog-bed", "variant_options": {"size": "L"}},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["page_mode"] == "family"
    assert data["parent_product"]["product_id"] == "example-orthopedic-dog-bed"
    assert data["resolution"]["status"] == "matched"
    assert data["selected_variant"]["sku_id"] == "ODB-GREY-L"


def test_ad_copy_context_returns_claim_boundaries() -> None:
    response = client.post("/context/ad-copy", json={"product_id": "example-orthopedic-dog-bed"})

    assert response.status_code == 200
    data = response.json()
    assert "supports joint comfort" in data["allowed_claims"]
    assert "clinically tested" in data["need_evidence"]
    assert "guaranteed pain relief" in data["forbidden_claims"]


def test_seo_context_returns_topics_and_faq_source() -> None:
    response = client.post("/context/seo", json={"product_id": "example-orthopedic-dog-bed"})

    assert response.status_code == 200
    data = response.json()
    assert "senior dogs" in data["topics"]
    assert "Can this bed help my senior dog" in data["faq_source"]
    assert data["long_tail_question_ideas"]


def test_context_returns_404_for_missing_product() -> None:
    response = client.post("/context/customer-support", json={"product_id": "missing-product"})

    assert response.status_code == 404


def test_context_returns_404_for_missing_sku() -> None:
    response = client.post(
        "/context/customer-support",
        json={"product_id": "example-orthopedic-dog-bed", "sku_id": "missing-sku"},
    )

    assert response.status_code == 404


def test_sources_are_available_to_downstream_agents() -> None:
    response = client.get("/products/example-orthopedic-dog-bed/sources")

    assert response.status_code == 200
    assert response.json() == []


def test_variant_resolve_endpoint_matches_identifier() -> None:
    response = client.post(
        "/products/example-orthopedic-dog-bed/variants/resolve",
        json={"identifier": "ODB-GREY-L"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "matched"
    assert response.json()["selected_variant"]["sku_id"] == "ODB-GREY-L"


def test_variant_page_requires_resolved_variant() -> None:
    response = client.post(
        "/context/listing",
        json={"product_id": "example-orthopedic-dog-bed", "page_mode": "variant"},
    )

    assert response.status_code == 409
