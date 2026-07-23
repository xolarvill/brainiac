from __future__ import annotations

import hashlib
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
    "sources.yaml",
    "golden-qa.yaml",
    "media/media.yaml",
]
RAW_SOURCE_DIRS = [
    "raw/supplier-docs",
    "raw/competitor-pages",
    "raw/customer-reviews",
    "raw/customer-support",
    "raw/interview-notes",
    "raw/media-inbox",
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


def load_sources(product_id: str, root: Path = ROOT) -> list[dict[str, Any]]:
    data = load_yaml(product_dir(product_id, root) / "sources.yaml")
    return data.get("sources", [])


def source_id_for_path(path: Path, root: Path = ROOT) -> str:
    product_root = root / "products" / path.relative_to(root / "products").parts[0]
    relative_path = path.relative_to(product_root).as_posix().encode("utf-8")
    return f"src_{hashlib.sha256(relative_path).hexdigest()[:12]}"


def source_kind_for_path(path: Path) -> str:
    return {
        ".csv": "table",
        ".html": "webpage",
        ".htm": "webpage",
        ".json": "structured-data",
        ".md": "text",
        ".rst": "text",
        ".txt": "text",
        ".tsv": "table",
        ".yaml": "structured-data",
        ".yml": "structured-data",
    }.get(path.suffix.lower(), path.suffix.lower().lstrip(".") or "file")


def readable_source(path: Path) -> bool:
    return path.suffix.lower() in {".csv", ".html", ".htm", ".json", ".md", ".rst", ".txt", ".tsv", ".yaml", ".yml"}


def read_source_text(path: Path) -> str | None:
    if not readable_source(path):
        return None
    try:
        return read_text(path)
    except UnicodeDecodeError:
        return None


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


def build_customer_support_context(
    product_id: str,
    sku_id: str | None = None,
    root: Path = ROOT,
    customer_question: str | None = None,
) -> dict[str, Any]:
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
        "retrieved_evidence": index_search(customer_question, root, product_id) if customer_question else [],
        "source_files": [
            f"products/{product_id}/product.yaml",
            f"products/{product_id}/variants.yaml",
            f"products/{product_id}/faq.md",
            f"products/{product_id}/care-guide.md",
            f"products/{product_id}/compliance.md",
            f"products/{product_id}/golden-qa.yaml",
            f"products/{product_id}/sources.yaml",
        ],
    }


def raw_search(query: str, root: Path = ROOT, product_id: str | None = None, limit: int = 20) -> list[dict[str, str]]:
    needle = query.lower()
    results: list[dict[str, str]] = []
    for folder in product_dirs(root):
        if product_id and folder.name != product_id:
            continue
        for path in list(folder.glob("*.md")) + list(folder.glob("*.yaml")) + list((folder / "media").glob("*.yaml")):
            text = read_text(path)
            if needle in text.lower():
                results.append(
                    {
                        "product_id": folder.name,
                        "source_id": f"kb_{hashlib.sha256(path.relative_to(root).as_posix().encode()).hexdigest()[:12]}",
                        "path": str(path.relative_to(root)),
                        "kind": "knowledge",
                        "snippet": text[:300],
                    }
                )
        for path in sorted(folder.joinpath("raw").rglob("*")):
            if not path.is_file():
                continue
            text = read_source_text(path)
            if text is None:
                continue
            if needle in text.lower():
                results.append(
                    {
                        "product_id": folder.name,
                        "source_id": source_id_for_path(path, root),
                        "path": str(path.relative_to(root)),
                        "kind": source_kind_for_path(path),
                        "snippet": text[:300],
                    }
                )
        if len(results) >= limit:
            return results[:limit]
    return results[:limit]


def index_search(query: str | None, root: Path = ROOT, product_id: str | None = None, limit: int = 20) -> list[dict[str, str]]:
    if not query or not query.strip():
        return []
    db_path = root / "indexes" / "product_kb.sqlite"
    if not db_path.exists():
        return raw_search(query, root, product_id, limit)
    tokens = [token for token in query.split() if token.strip()]
    fts_query = " OR ".join(f'"{token.replace(chr(34), "")}"' for token in tokens)
    with sqlite3.connect(db_path) as db:
        try:
            rows = db.execute(
                "select product_id, source_id, path, kind, snippet(docs_fts, 4, '[', ']', '...', 16) "
                "from docs_fts where docs_fts match ? "
                + ("and product_id = ? " if product_id else "")
                + "limit ?",
                (fts_query, product_id, limit) if product_id else (fts_query, limit),
            ).fetchall()
            return [
                {"product_id": product, "source_id": source, "path": path, "kind": kind, "snippet": snippet}
                for product, source, path, kind, snippet in rows
            ]
        except sqlite3.Error:
            try:
                rows = db.execute(
                    "select product_id, source_id, path, kind, content from docs where lower(content) like ? "
                    + ("and product_id = ? " if product_id else "")
                    + "limit ?",
                    (f"%{query.lower()}%", product_id, limit) if product_id else (f"%{query.lower()}%", limit),
                ).fetchall()
                return [
                    {"product_id": product, "source_id": source, "path": path, "kind": kind, "snippet": content[:300]}
                    for product, source, path, kind, content in rows
                ]
            except sqlite3.Error:
                return raw_search(query, root, product_id, limit)
