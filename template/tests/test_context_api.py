from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import app


def test_customer_support_context_returns_claim_boundaries() -> None:
    client = TestClient(app)
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
