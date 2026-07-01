from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from kb import load_product, markdown_bundle, product_dirs


def clean_forbidden(text: str, forbidden: list[str]) -> str:
    cleaned = text
    for claim in forbidden:
        cleaned = cleaned.replace(claim, "[removed forbidden claim]")
    return cleaned


def main() -> int:
    out_dir = ROOT / "exports" / "shopify"
    out_dir.mkdir(parents=True, exist_ok=True)
    for folder in product_dirs(ROOT):
        product = load_product(folder.name, ROOT)
        modules = markdown_bundle(folder.name, ROOT)
        body = [
            f"# {product['product_name']}",
            "",
            product.get("brand_positioning", {}).get("target_customer", ""),
            "",
            "## Highlights",
            *[f"- {claim}" for claim in product.get("claims_allowed", [])],
            "",
            "## FAQ",
            modules["faq.md"],
        ]
        text = clean_forbidden("\n".join(body), product.get("claims_forbidden", []))
        (out_dir / f"{folder.name}.md").write_text(text + "\n", encoding="utf-8")
    print(f"Exported Shopify snippets to {out_dir.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
