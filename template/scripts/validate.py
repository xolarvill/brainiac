from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from kb import RAW_SOURCE_DIRS, REQUIRED_PRODUCT_FILES, load_yaml, product_dirs


def validate_schema(data: object, schema_path: Path) -> list[str]:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    return [error.message for error in validator.iter_errors(data)]


def validate_product(folder: Path) -> list[str]:
    errors: list[str] = []
    for name in REQUIRED_PRODUCT_FILES:
        if not (folder / name).exists():
            errors.append(f"{folder.name}: missing {name}")
    for name in RAW_SOURCE_DIRS:
        if not (folder / name).is_dir():
            errors.append(f"{folder.name}: missing raw source directory {name}")

    schema_map = {
        "product.yaml": "product.schema.json",
        "variants.yaml": "variants.schema.json",
        "media/media.yaml": "media.schema.json",
        "golden-qa.yaml": "golden-qa.schema.json",
    }
    for data_file, schema_file in schema_map.items():
        path = folder / data_file
        if path.exists():
            for message in validate_schema(load_yaml(path), ROOT / "schemas" / schema_file):
                errors.append(f"{folder.name}/{data_file}: {message}")

    variants = load_yaml(folder / "variants.yaml").get("variants", [])
    media = load_yaml(folder / "media" / "media.yaml").get("assets", [])
    asset_ids = {asset.get("asset_id") for asset in media}
    for variant in variants:
        for asset_id in variant.get("media_refs", []):
            if asset_id not in asset_ids:
                errors.append(f"{folder.name}: {variant.get('sku_id')} references missing media asset {asset_id}")

    for asset in media:
        if asset.get("type") == "video" and asset.get("transcript_path"):
            transcript = folder / asset["transcript_path"]
            if not transcript.exists():
                errors.append(f"{folder.name}: missing transcript {asset['transcript_path']}")

    sku_ids = [variant.get("sku_id") for variant in variants]
    duplicates = sorted({sku_id for sku_id in sku_ids if sku_ids.count(sku_id) > 1})
    for sku_id in duplicates:
        errors.append(f"{folder.name}: duplicate sku_id {sku_id}")

    return errors


def main() -> int:
    errors: list[str] = []
    for folder in product_dirs(ROOT):
        errors.extend(validate_product(folder))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
