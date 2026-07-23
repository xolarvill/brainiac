from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from kb import load_yaml, write_yaml


def parse_pairs(values: list[str]) -> dict[str, object]:
    result: dict[str, object] = {}
    for value in values:
        key, separator, raw_value = value.partition("=")
        if not separator or not key.strip():
            raise ValueError(f"Expected KEY=VALUE, got: {value}")
        result[key.strip()] = yaml.safe_load(raw_value)
    return result


def parse_evidence(values: list[str]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for value in values:
        key, separator, source_id = value.partition("=")
        if not separator or not key.strip() or not source_id.strip():
            raise ValueError(f"Expected FIELD=SOURCE_ID, got: {value}")
        result.setdefault(key.strip(), []).append(source_id.strip())
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Add a product variant to variants.yaml.")
    parser.add_argument("product_id")
    parser.add_argument("sku_id")
    parser.add_argument("--model-number")
    parser.add_argument("--alias", action="append", default=[])
    parser.add_argument("--option", action="append", default=[], metavar="KEY=VALUE")
    parser.add_argument("--attribute", action="append", default=[], metavar="KEY=VALUE")
    parser.add_argument("--source-ref", action="append", default=[])
    parser.add_argument("--evidence", action="append", default=[], metavar="FIELD=SOURCE_ID")
    parser.add_argument("--media-ref", action="append", default=[])
    args = parser.parse_args()

    path = ROOT / "products" / args.product_id / "variants.yaml"
    if not path.exists():
        print(f"Missing variants file: {path}", file=sys.stderr)
        return 1

    try:
        options = parse_pairs(args.option)
        attributes = parse_pairs(args.attribute)
        evidence = parse_evidence(args.evidence)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    data = load_yaml(path)
    variants = data.setdefault("variants", [])
    if any(item.get("sku_id") == args.sku_id for item in variants):
        print(f"Duplicate sku_id: {args.sku_id}", file=sys.stderr)
        return 1

    variant = {
        "sku_id": args.sku_id,
        "parent_product_id": args.product_id,
        "options": options,
        "attributes": attributes,
        "aliases": args.alias,
        "source_refs": args.source_ref,
        "evidence": evidence,
        "media_refs": args.media_ref,
    }
    if args.model_number:
        variant["model_number"] = args.model_number
    axes = data.setdefault("variant_axes", [])
    known_axes = {axis.get("key") for axis in axes}
    for key, value in options.items():
        if key in known_axes:
            continue
        axes.append(
            {
                "key": key,
                "label": key.replace("_", " ").title(),
                "value_type": "number" if isinstance(value, (int, float)) and not isinstance(value, bool) else "string",
            }
        )
        known_axes.add(key)
    variants.append(variant)
    write_yaml(path, data)
    print(f"Added {args.sku_id} to {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
