from __future__ import annotations

import argparse
import hashlib
import mimetypes
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from kb import product_dir, read_source_text, source_id_for_path, source_kind_for_path, write_yaml


def copy_into_raw(source: Path, raw_dir: Path) -> None:
    destination_root = raw_dir / "imported"
    if source == raw_dir or raw_dir in source.parents:
        raise ValueError("Source path is already inside the product raw directory")
    if source.is_file():
        destination_root.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination_root / source.name)
        return

    if not source.is_dir():
        raise FileNotFoundError(f"Source path does not exist: {source}")
    for path in sorted(item for item in source.rglob("*") if item.is_file()):
        relative = path.relative_to(source)
        destination = destination_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)


def ingest_product_sources(product_id: str, root: Path = ROOT, source: Path | None = None) -> list[dict[str, object]]:
    folder = product_dir(product_id, root)
    if not folder.is_dir():
        raise FileNotFoundError(f"Product not found: {product_id}")

    raw_dir = folder / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    if source is not None:
        copy_into_raw(source.resolve(), raw_dir)

    records: list[dict[str, object]] = []
    for path in sorted(item for item in raw_dir.rglob("*") if item.is_file() and item.name != ".gitkeep"):
        relative = path.relative_to(folder).as_posix()
        stat = path.stat()
        readable = read_source_text(path) is not None
        records.append(
            {
                "source_id": source_id_for_path(path, root),
                "path": relative,
                "kind": source_kind_for_path(path),
                "mime_type": mimetypes.guess_type(path.name)[0] or "application/octet-stream",
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "size_bytes": stat.st_size,
                "readable": readable,
                "modified_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
            }
        )

    write_yaml(folder / "sources.yaml", {"sources": records})
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description="Register and index product source files.")
    parser.add_argument("product_id")
    parser.add_argument("source", nargs="?", type=Path, help="Optional file or folder to copy into raw/imported.")
    args = parser.parse_args()

    try:
        records = ingest_product_sources(args.product_id, ROOT, args.source)
        from scripts.build_index import build_index

        build_index(ROOT)
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Registered {len(records)} source file(s) and rebuilt indexes/product_kb.sqlite")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
