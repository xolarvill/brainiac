from __future__ import annotations

import json
import hashlib
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from kb import (
    RAW_SOURCE_DIRS,
    REQUIRED_PRODUCT_FILES,
    load_yaml,
    product_dirs,
    referenced_source_ids,
    variant_identifier_values,
    variant_options,
)


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
        "sources.yaml": "source.schema.json",
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

    axes = load_yaml(folder / "variants.yaml").get("variant_axes", [])
    axis_keys = [axis.get("key") for axis in axes]
    for key in sorted({key for key in axis_keys if key and axis_keys.count(key) > 1}):
        errors.append(f"{folder.name}: duplicate variant axis {key}")
    declared_axes = {key for key in axis_keys if key}
    identifiers: dict[str, str] = {}
    for variant in variants:
        if variant.get("parent_product_id") and variant["parent_product_id"] != folder.name:
            errors.append(f"{folder.name}: variant {variant.get('sku_id')} has wrong parent_product_id")
        options = variant_options(variant, axes)
        if declared_axes and set(options) - declared_axes:
            extra = sorted(set(options) - declared_axes)
            errors.append(f"{folder.name}: {variant.get('sku_id')} uses undeclared variant axes: {', '.join(extra)}")
        missing = sorted(declared_axes - set(options))
        if missing:
            errors.append(f"{folder.name}: {variant.get('sku_id')} is missing variant axes: {', '.join(missing)}")
        for identifier in variant_identifier_values(variant):
            normalized = "".join(character for character in identifier.lower() if character.isalnum())
            previous = identifiers.get(normalized)
            if previous and previous != variant.get("sku_id"):
                errors.append(f"{folder.name}: duplicate variant identifier {identifier}")
            identifiers[normalized] = str(variant.get("sku_id"))

    source_records = load_yaml(folder / "sources.yaml").get("sources", [])
    source_ids = [record.get("source_id") for record in source_records]
    known_source_ids = {source_id for source_id in source_ids if source_id}
    source_paths = [record.get("path") for record in source_records]
    for value, label in [(source_ids, "source_id"), (source_paths, "source path")]:
        duplicates = sorted({item for item in value if item and value.count(item) > 1})
        for item in duplicates:
            errors.append(f"{folder.name}: duplicate {label} {item}")
    for record in source_records:
        relative = record.get("path", "")
        path = folder / relative
        if not relative.startswith("raw/") or ".." in Path(relative).parts:
            errors.append(f"{folder.name}: source path must stay under raw/: {relative}")
            continue
        if not path.is_file():
            errors.append(f"{folder.name}: missing source file {relative}")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != record.get("sha256"):
            errors.append(f"{folder.name}: source changed since ingest, rerun scripts/ingest_sources.py: {relative}")

    product = load_yaml(folder / "product.yaml")
    for source_id in referenced_source_ids(product):
        if source_id not in known_source_ids:
            errors.append(f"{folder.name}/product.yaml: unknown source reference {source_id}")
    for variant in variants:
        for source_id in referenced_source_ids(variant):
            if source_id not in known_source_ids:
                errors.append(
                    f"{folder.name}/variants.yaml: {variant.get('sku_id')} references unknown source {source_id}"
                )

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
