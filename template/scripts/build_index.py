from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from kb import MARKDOWN_MODULES, load_media, load_product, load_variants, product_dirs, read_text


def docs_for_product(folder: Path) -> list[tuple[str, str, str]]:
    product_id = folder.name
    docs = [
        (product_id, f"products/{product_id}/product.yaml", str(load_product(product_id, ROOT))),
        (product_id, f"products/{product_id}/variants.yaml", str(load_variants(product_id, ROOT))),
        (product_id, f"products/{product_id}/media/media.yaml", str(load_media(product_id, ROOT))),
    ]
    for name in MARKDOWN_MODULES:
        docs.append((product_id, f"products/{product_id}/{name}", read_text(folder / name)))
    for transcript in (folder / "media" / "transcripts").glob("*.md"):
        docs.append((product_id, str(transcript.relative_to(ROOT)), read_text(transcript)))
    return docs


def main() -> int:
    db_path = ROOT / "indexes" / "product_kb.sqlite"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as db:
        db.execute("drop table if exists docs")
        db.execute("create table docs(product_id text, path text primary key, content text)")
        for folder in product_dirs(ROOT):
            db.executemany("insert into docs(product_id, path, content) values (?, ?, ?)", docs_for_product(folder))
        try:
            db.execute("drop table if exists docs_fts")
            db.execute("create virtual table docs_fts using fts5(product_id, path, content)")
            db.execute("insert into docs_fts(product_id, path, content) select product_id, path, content from docs")
        except sqlite3.Error as exc:
            print(f"FTS5 unavailable, plain docs table built: {exc}")
        db.commit()
    print(f"Built {db_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
