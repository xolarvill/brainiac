from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from kb import load_yaml, write_yaml


def main() -> int:
    parser = argparse.ArgumentParser(description="Add a SKU variant to variants.yaml.")
    parser.add_argument("product_id")
    parser.add_argument("sku_id")
    parser.add_argument("--size", required=True)
    parser.add_argument("--color", required=True)
    parser.add_argument("--length-cm", type=float, required=True)
    parser.add_argument("--width-cm", type=float, required=True)
    parser.add_argument("--height-cm", type=float, required=True)
    parser.add_argument("--min-weight-kg", type=float, required=True)
    parser.add_argument("--max-weight-kg", type=float, required=True)
    parser.add_argument("--media-ref", action="append", default=[])
    args = parser.parse_args()

    path = ROOT / "products" / args.product_id / "variants.yaml"
    if not path.exists():
        print(f"Missing variants file: {path}", file=sys.stderr)
        return 1

    data = load_yaml(path)
    variants = data.setdefault("variants", [])
    if any(item.get("sku_id") == args.sku_id for item in variants):
        print(f"Duplicate sku_id: {args.sku_id}", file=sys.stderr)
        return 1

    variants.append(
        {
            "sku_id": args.sku_id,
            "size": args.size,
            "color": args.color,
            "dimensions_cm": {
                "length": args.length_cm,
                "width": args.width_cm,
                "height": args.height_cm,
            },
            "recommended_pet_weight_kg": {
                "min": args.min_weight_kg,
                "max": args.max_weight_kg,
            },
            "suitable_breeds": [],
            "media_refs": args.media_ref,
        }
    )
    write_yaml(path, data)
    print(f"Added {args.sku_id} to {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
