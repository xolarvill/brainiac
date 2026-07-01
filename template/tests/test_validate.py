from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from kb import load_media, load_variants, product_dir
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
