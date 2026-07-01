from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from kb import CONFLICT_SCAN_FILES, load_yaml, product_dirs, read_text


DIMENSION_RE = re.compile(r"\b(?P<sku>[A-Z0-9-]+)\b[^.\n]*(?P<l>\d+(?:\.\d+)?)\s*[xX]\s*(?P<w>\d+(?:\.\d+)?)\s*[xX]\s*(?P<h>\d+(?:\.\d+)?)")


def main() -> int:
    errors: list[str] = []
    for folder in product_dirs(ROOT):
        product = load_yaml(folder / "product.yaml")
        forbidden = [claim.lower() for claim in product.get("claims_forbidden", [])]
        if not product.get("claims_forbidden") or not product.get("support_boundaries"):
            errors.append(f"{folder.name}: missing claim boundaries")

        for name in CONFLICT_SCAN_FILES:
            text = read_text(folder / name).lower()
            for claim in forbidden:
                if claim and forbidden_claim_used(text, claim):
                    errors.append(f"{folder.name}/{name}: forbidden claim appears: {claim}")

        variants = load_yaml(folder / "variants.yaml").get("variants", [])
        expected = {
            item["sku_id"]: (
                str(item["dimensions_cm"]["length"]),
                str(item["dimensions_cm"]["width"]),
                str(item["dimensions_cm"]["height"]),
            )
            for item in variants
        }
        for name in ["faq.md", "objections.md", "care-guide.md", "comparison.md"]:
            for match in DIMENSION_RE.finditer(read_text(folder / name)):
                sku_id = match.group("sku")
                found = (match.group("l"), match.group("w"), match.group("h"))
                if sku_id in expected and found != expected[sku_id]:
                    errors.append(f"{folder.name}/{name}: stale dimensions for {sku_id}: {'x'.join(found)}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Conflict check passed")
    return 0


def forbidden_claim_used(text: str, claim: str) -> bool:
    for match in re.finditer(re.escape(claim), text):
        prefix = text[max(0, match.start() - 40) : match.start()]
        if re.search(r"\b(no|not|cannot|can't|never|must not|do not|does not)\b", prefix):
            continue
        return True
    return False


if __name__ == "__main__":
    raise SystemExit(main())
