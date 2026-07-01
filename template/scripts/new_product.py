from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from kb import load_yaml, write_yaml


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a product folder from products/_template.")
    parser.add_argument("slug", help="Product slug, e.g. orthopedic-dog-bed")
    parser.add_argument("--name", help="Human-readable product name")
    args = parser.parse_args()

    source = ROOT / "products" / "_template"
    target = ROOT / "products" / args.slug
    if target.exists():
        print(f"Product already exists: {target}", file=sys.stderr)
        return 1

    shutil.copytree(source, target)
    product_path = target / "product.yaml"
    product = load_yaml(product_path)
    product["product_id"] = args.slug
    product["product_name"] = args.name or args.slug.replace("-", " ").title()
    write_yaml(product_path, product)
    print(f"Created {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
