from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from kb import (
    MARKDOWN_MODULES,
    load_media,
    load_product,
    load_sources,
    load_variants,
    product_dirs,
    read_source_text,
    source_id_for_path,
    source_kind_for_path,
    read_text,
)


def docs_for_product(folder: Path, root: Path = ROOT) -> list[tuple[str, str, str, str, str]]:
    product_id = folder.name
    docs = [
        (product_id, f"kb_{product_id}_product", f"products/{product_id}/product.yaml", "knowledge", str(load_product(product_id, root))),
        (product_id, f"kb_{product_id}_variants", f"products/{product_id}/variants.yaml", "knowledge", str(load_variants(product_id, root))),
        (product_id, f"kb_{product_id}_media", f"products/{product_id}/media/media.yaml", "knowledge", str(load_media(product_id, root))),
    ]
    for name in MARKDOWN_MODULES:
        docs.append((product_id, f"kb_{product_id}_{name}", f"products/{product_id}/{name}", "knowledge", read_text(folder / name)))
    for transcript in (folder / "media" / "transcripts").glob("*.md"):
        docs.append((product_id, f"kb_{product_id}_{transcript.stem}", str(transcript.relative_to(root)), "knowledge", read_text(transcript)))
    source_records = {record["path"]: record for record in load_sources(product_id, root)}
    for path in sorted(folder.joinpath("raw").rglob("*")):
        if not path.is_file():
            continue
        text = read_source_text(path)
        if text is None:
            continue
        relative = path.relative_to(folder).as_posix()
        record = source_records.get(relative, {})
        docs.append(
            (
                product_id,
                str(record.get("source_id") or source_id_for_path(path, root)),
                str(path.relative_to(root)),
                str(record.get("kind") or source_kind_for_path(path)),
                text,
            )
        )
    return docs


def build_index(root: Path = ROOT) -> Path:
    db_path = root / "indexes" / "product_kb.sqlite"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as db:
        db.execute("drop table if exists docs")
        db.execute("create table docs(product_id text, source_id text, path text primary key, kind text, content text)")
        for folder in product_dirs(root):
            db.executemany(
                "insert into docs(product_id, source_id, path, kind, content) values (?, ?, ?, ?, ?)",
                docs_for_product(folder, root),
            )
        try:
            db.execute("drop table if exists docs_fts")
            db.execute("create virtual table docs_fts using fts5(product_id, source_id, path, kind, content)")
            db.execute("insert into docs_fts(product_id, source_id, path, kind, content) select product_id, source_id, path, kind, content from docs")
        except sqlite3.Error as exc:
            print(f"FTS5 unavailable, plain docs table built: {exc}")
        db.commit()
    return db_path


def main() -> int:
    db_path = build_index(ROOT)
    print(f"Built {db_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
