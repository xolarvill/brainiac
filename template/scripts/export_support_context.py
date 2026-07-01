from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from kb import build_customer_support_context, load_variants, product_dirs, write_json


def main() -> int:
    out_dir = ROOT / "exports" / "customer-support"
    for folder in product_dirs(ROOT):
        context = build_customer_support_context(folder.name, None, ROOT)
        write_json(out_dir / f"{folder.name}.json", context)
        for variant in load_variants(folder.name, ROOT):
            write_json(out_dir / f"{folder.name}-{variant['sku_id']}.json", build_customer_support_context(folder.name, variant["sku_id"], ROOT))
    print(f"Exported customer support contexts to {out_dir.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
