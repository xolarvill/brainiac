from __future__ import annotations

import sys
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from kb import load_media, load_variants, load_yaml, product_dir, source_evidence, write_yaml
from scripts.check_conflicts import forbidden_claim_used
from scripts.validate import validate_product


def test_required_product_files_and_schemas_are_valid() -> None:
    assert validate_product(product_dir("example-orthopedic-dog-bed")) == []


def test_variant_media_refs_exist() -> None:
    media_ids = {asset["asset_id"] for asset in load_media("example-orthopedic-dog-bed")["assets"]}
    for variant in load_variants("example-orthopedic-dog-bed"):
        assert set(variant["media_refs"]) <= media_ids


def test_forbidden_claim_detection_allows_negated_usage() -> None:
    assert forbidden_claim_used("This cures arthritis.", "cures arthritis")
    assert not forbidden_claim_used("No, this cannot cure arthritis.", "cure arthritis")


def test_source_references_are_validated_and_exposed(tmp_path: Path) -> None:
    product_id = "source-backed-product"
    product_folder = tmp_path / "products" / product_id
    shutil.copytree(ROOT / "products" / "_template", product_folder)
    source_file = product_folder / "raw" / "supplier-docs" / "spec.txt"
    source_file.write_text("The camera has a 20MP sensor.", encoding="utf-8")

    from scripts.ingest_sources import ingest_product_sources

    source_id = ingest_product_sources(product_id, tmp_path)[0]["source_id"]
    product = load_yaml(product_folder / "product.yaml")
    product["source_refs"] = [source_id]
    product["evidence"] = {"common_facts.sensor": [source_id]}
    write_yaml(product_folder / "product.yaml", product)
    variant_data = load_yaml(product_folder / "variants.yaml")
    variant_data["variants"] = [{"sku_id": "CAM-20", "source_refs": [source_id], "media_refs": []}]
    write_yaml(product_folder / "variants.yaml", variant_data)

    assert validate_product(product_folder) == []
    evidence = source_evidence(product_id, variant_data["variants"][0], tmp_path)
    assert {item["scope"] for item in evidence} == {"product", "variant:CAM-20"}
    assert all(item["path"] == "raw/supplier-docs/spec.txt" for item in evidence)

    product["source_refs"] = ["src_000000000000"]
    write_yaml(product_folder / "product.yaml", product)
    assert any("unknown source reference" in error for error in validate_product(product_folder))
