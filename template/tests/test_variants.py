from __future__ import annotations

import shutil
from pathlib import Path

from kb import load_yaml, resolve_variant, write_yaml
from scripts.validate import validate_product


ROOT = Path(__file__).resolve().parents[1]


def test_generic_variant_axes_resolve_units_and_ambiguity(tmp_path: Path) -> None:
    product_id = "fixed-aperture-camera"
    product_folder = tmp_path / "products" / product_id
    shutil.copytree(ROOT / "products" / "_template", product_folder)
    product = load_yaml(product_folder / "product.yaml")
    product["product_id"] = product_id
    product["product_name"] = "Fixed Aperture Camera"
    write_yaml(product_folder / "product.yaml", product)
    write_yaml(
        product_folder / "variants.yaml",
        {
            "variant_axes": [
                {"key": "resolution_mp", "label": "Resolution", "value_type": "number", "unit": "MP"},
                {"key": "focal_length_mm", "label": "Focal Length", "value_type": "number", "unit": "mm"},
            ],
            "variants": [
                {
                    "sku_id": "FAC-20-12",
                    "model_number": "FAC-20-12",
                    "aliases": ["20MP 12mm"],
                    "options": {"resolution_mp": 20, "focal_length_mm": 12},
                    "media_refs": [],
                },
                {
                    "sku_id": "FAC-20-28",
                    "model_number": "FAC-20-28",
                    "options": {"resolution_mp": 20, "focal_length_mm": 28},
                    "media_refs": [],
                },
            ],
        },
    )

    assert validate_product(product_folder) == []
    assert resolve_variant(product_id, "20MP 12mm", root=tmp_path)["selected_variant"]["sku_id"] == "FAC-20-12"
    assert resolve_variant(product_id, options={"resolution_mp": "20MP"}, root=tmp_path)["status"] == "ambiguous"
    assert resolve_variant(
        product_id,
        options={"resolution_mp": "20MP", "focal_length_mm": "12mm"},
        root=tmp_path,
    )["selected_variant"]["sku_id"] == "FAC-20-12"
