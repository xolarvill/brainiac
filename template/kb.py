from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent
PRODUCTS_DIR = ROOT / "products"
REQUIRED_PRODUCT_FILES = [
    "product.yaml",
    "variants.yaml",
    "faq.md",
    "objections.md",
    "care-guide.md",
    "compliance.md",
    "comparison.md",
    "source-notes.md",
    "golden-qa.yaml",
    "media/media.yaml",
]
MARKDOWN_MODULES = [
    "faq.md",
    "objections.md",
    "care-guide.md",
    "compliance.md",
    "comparison.md",
    "source-notes.md",
]
CONFLICT_SCAN_FILES = [
    "faq.md",
    "objections.md",
    "care-guide.md",
    "comparison.md",
]


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def write_yaml(path: Path, data: Any) -> None:
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=True)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def product_dirs(root: Path = ROOT) -> list[Path]:
    products = root / "products"
    return sorted(path for path in products.iterdir() if path.is_dir() and path.name != "_template")


def product_dir(product_id: str, root: Path = ROOT) -> Path:
    return root / "products" / product_id


def load_product(product_id: str, root: Path = ROOT) -> dict[str, Any]:
    return load_yaml(product_dir(product_id, root) / "product.yaml")


def load_variants(product_id: str, root: Path = ROOT) -> list[dict[str, Any]]:
    data = load_yaml(product_dir(product_id, root) / "variants.yaml")
    return data.get("variants", [])


def load_media(product_id: str, root: Path = ROOT) -> dict[str, Any]:
    return load_yaml(product_dir(product_id, root) / "media" / "media.yaml")


def load_golden_qa(product_id: str, root: Path = ROOT) -> list[dict[str, Any]]:
    data = load_yaml(product_dir(product_id, root) / "golden-qa.yaml")
    return data if isinstance(data, list) else []


def find_variant(product_id: str, sku_id: str | None, root: Path = ROOT) -> dict[str, Any]:
    if not sku_id:
        return {}
    for variant in load_variants(product_id, root):
        if variant.get("sku_id") == sku_id:
            return variant
    return {}


def markdown_bundle(product_id: str, root: Path = ROOT) -> dict[str, str]:
    folder = product_dir(product_id, root)
    return {name: read_text(folder / name) for name in MARKDOWN_MODULES}


def build_customer_support_context(product_id: str, sku_id: str | None = None, root: Path = ROOT) -> dict[str, Any]:
    product = load_product(product_id, root)
    return {
        "product_id": product_id,
        "sku_id": sku_id,
        "relevant_facts": [
            {"product_name": product.get("product_name")},
            {"common_facts": product.get("common_facts", {})},
            {"materials": product.get("materials", {})},
            {"washing": product.get("washing", {})},
        ],
        "variant_facts": find_variant(product_id, sku_id, root),
        "care_instructions": read_text(product_dir(product_id, root) / "care-guide.md").splitlines(),
        "claim_boundaries": {
            "allowed": product.get("claims_allowed", []),
            "need_evidence": product.get("claims_need_evidence", []),
            "forbidden": product.get("claims_forbidden", []),
        },
        "suggested_answer_style": "helpful, cautious, non-medical",
        "must_not_say": product.get("claims_forbidden", []),
        "golden_qa": load_golden_qa(product_id, root),
        "source_files": [
            f"products/{product_id}/product.yaml",
            f"products/{product_id}/variants.yaml",
            f"products/{product_id}/faq.md",
            f"products/{product_id}/care-guide.md",
            f"products/{product_id}/compliance.md",
            f"products/{product_id}/golden-qa.yaml",
        ],
    }


def raw_search(query: str, root: Path = ROOT) -> list[dict[str, str]]:
    needle = query.lower()
    results: list[dict[str, str]] = []
    for folder in product_dirs(root):
        for path in list(folder.glob("*.md")) + list(folder.glob("*.yaml")) + list((folder / "media").glob("*.yaml")):
            text = read_text(path)
            if needle in text.lower():
                results.append({"path": str(path.relative_to(root)), "snippet": text[:300]})
    return results


def index_search(query: str, root: Path = ROOT) -> list[dict[str, str]]:
    db_path = root / "indexes" / "product_kb.sqlite"
    if not db_path.exists():
        return raw_search(query, root)
    with sqlite3.connect(db_path) as db:
        try:
            rows = db.execute(
                "select path, snippet(docs_fts, 2, '[', ']', '...', 16) from docs_fts where docs_fts match ? limit 20",
                (query,),
            ).fetchall()
            return [{"path": path, "snippet": snippet} for path, snippet in rows]
        except sqlite3.Error:
            rows = db.execute(
                "select path, content from docs where lower(content) like ? limit 20",
                (f"%{query.lower()}%",),
            ).fetchall()
            return [{"path": path, "snippet": content[:300]} for path, content in rows]
