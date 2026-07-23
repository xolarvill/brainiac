from __future__ import annotations

import shutil
from pathlib import Path

from kb import index_search, load_sources
from scripts.build_index import build_index
from scripts.ingest_sources import ingest_product_sources
from scripts.validate import validate_product


ROOT = Path(__file__).resolve().parents[1]


def test_ingest_registers_and_indexes_raw_text(tmp_path: Path) -> None:
    product_id = "sample-product"
    product_folder = tmp_path / "products" / product_id
    shutil.copytree(ROOT / "products" / "_template", product_folder)
    source_file = product_folder / "raw" / "supplier-docs" / "spec.txt"
    source_file.write_text("The removable cover is machine washable.", encoding="utf-8")

    records = ingest_product_sources(product_id, tmp_path)
    build_index(tmp_path)

    assert records[0]["path"] == "raw/supplier-docs/spec.txt"
    assert load_sources(product_id, tmp_path)[0]["sha256"]
    results = index_search("machine washable", tmp_path, product_id)
    assert results[0]["source_id"] == records[0]["source_id"]
    assert results[0]["kind"] == "text"


def test_validation_detects_changed_source(tmp_path: Path) -> None:
    product_id = "sample-product"
    product_folder = tmp_path / "products" / product_id
    shutil.copytree(ROOT / "products" / "_template", product_folder)
    source_file = product_folder / "raw" / "supplier-docs" / "spec.txt"
    source_file.write_text("Initial specification.", encoding="utf-8")

    ingest_product_sources(product_id, tmp_path)
    source_file.write_text("Changed specification.", encoding="utf-8")

    errors = validate_product(product_folder)
    assert any("source changed since ingest" in error for error in errors)
